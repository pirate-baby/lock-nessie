import json
import os
import signal
from typing import TYPE_CHECKING
import multiprocessing
import click
import uvicorn
from settings import EnvSettings, ConfigSettings, OpenIDIssuer

if TYPE_CHECKING:
    from pathlib import Path

env_settings = EnvSettings()

@click.group()
def cli():
    """Lock Nessie CLI"""

@cli.group()
def config():
    """Configure Lock Nessie settings."""

@config.command()
def init():
    """Initialize a new config file"""
    config_file = env_settings.config_path / "config.json"
    config_dict = {}
    click.echo(f"Initializing new config file at {config_file}")

    if config_file.exists():
        click.echo(f"Config file already exists at {config_file}")
        return
    config_file.parent.mkdir(parents=True, exist_ok=True)

    config_dict["openid_issuer"] = click.prompt("Which OpenID provider are you using?", type=click.Choice(OpenIDIssuer.values()))
    match config_dict["openid_issuer"]:
        case OpenIDIssuer.microsoft:
            config_dict["openid_client_id"] = click.prompt("What is your Microsoft client ID?", type=str)
        case _:
            click.echo("That provider is not supported yet")
    _ = _sync_config_settings(config_dict, config_file)
    click.echo(f"Config file initialized at {config_file}. See {config_file} to modify or update the configurations.")

@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):
    """Set a config value"""
    config_file = env_settings.config_path / "config.json"
    config_settings = ConfigSettings()
    try:
        setattr(config_settings, key, value)
    except AttributeError:
        click.echo(f"Invalid config key: {key}")
        return
    _ = _sync_config_settings(config_settings.model_dump(), config_file)
    click.echo(f"Config file updated at {config_file}. See {config_file} to modify or update the configurations.")

@cli.group()
def service():
    """Manage the Lock Nessie HTTP service."""

@service.command()
@click.option("--port", type=int, default=env_settings.auth_callback_port, help="The port to run the HTTP service on")
@click.option("--host", type=str, default="0.0.0.0", help="The host to run the HTTP service on")
@click.option("--daemon", is_flag=True, help="Run the HTTP service as a daemon")
def start(port: int, host: str, daemon: bool):
    """Start the HTTP service."""
    if daemon:
        process = multiprocessing.Process(target=_start_server, args=(port, host))
        pid = process.start()
        pid_cache = env_settings.config_path / "pid"
        pid_cache.write_text(str(pid))
        click.echo(f"HTTP service started on {host}:{port} with PID {pid}")
    else:
        _start_server(port, host)


@service.command()
@click.option("--kill", is_flag=True, help="Send a SIGKILL signal to the HTTP service. Useful if the server refuses to stop.")
def stop(kill: bool):
    """Stop the HTTP service."""
    sig_enum = "SIGKILL" if kill else "SIGINT"
    sig = getattr(signal, sig_enum)
    pid_cache = env_settings.config_path / "pid"
    if not pid_cache.exists():
        click.echo("HTTP service is not running")
        return
    pid = int(pid_cache.read_text())
    click.echo(f"Terminating HTTP service with PID {pid} with signal {sig_enum}")
    _stop_server(pid, sig)
    click.echo(f"HTTP service {sig_enum} stop signal sent")

@cli.group()
def token():
    """Manage OpenID tokens."""

@token.command()
def show():
    """Show the active OpenID bearer token."""
    from main import LockNessie
    token = LockNessie().get_token()
    click.echo(token)


def _sync_config_settings(initial_config_dict: dict, config_file: Path) -> None:
    """round-about way to populate the config defaults to make user input easier
    by exposing them in the config file.

    Args:
        initial_config_dict: the required values that the config object needs to be populated with
        config_file: the path to the config file to be written to
    """
    config_file.write_text(json.dumps(initial_config_dict, indent=4))
    # read back with all the defaults
    synced_config_settings = ConfigSettings().model_dump()
    # get rid of env vars
    del synced_config_settings["env"]
    # write back with all the defaults to the config file
    config_file.write_text(json.dumps(synced_config_settings, indent=4))


def _start_server(port: int, host: str):
    """Start the HTTP service."""
    from server import app
    uvicorn.run(app, host=host, port=port)

def _stop_server(pid: int, sig: int):
    """Stop the HTTP service."""
    os.kill(pid, sig)

if __name__ == "__main__":
    cli()