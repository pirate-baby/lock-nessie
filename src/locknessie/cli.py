import json
from pathlib import Path
import os
import signal
from typing import TYPE_CHECKING
import multiprocessing
import click
from pydantic import ValidationError
import uvicorn
from locknessie.settings import safely_get_settings, OpenIDIssuer, NoConfigError, get_config_path
import functools
from locknessie.settings import ConfigSettings

if TYPE_CHECKING:
    from pathlib import Path

def add_config_options(command):
    for field_name, field in ConfigSettings.model_fields.items():
        if field_name == "config_path":
            continue
        option_name = f"--{field_name.replace('_', '-')}"
        option_kwargs = {"default": None, "help": f"Config option for {field_name}"}
        if hasattr(field, 'annotation'):
            option_kwargs["type"] = field.annotation if field.annotation in [int, str, bool] else str
        command = click.option(option_name, **option_kwargs)(command)
    return command

def _filter_none_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}

def _sync_config_settings(initial_config_dict: dict, config_file: "Path") -> None:
    """round-about way to populate the config defaults to make user input easier
    by exposing them in the config file.

    Args:
        initial_config_dict: the required values that the config object needs to be populated with
        config_file: the path to the config file to be written to
    """
    # hack to deal with serialization issues
    for key, value in initial_config_dict.items():
        if isinstance(value, Path):
            initial_config_dict[key] = str(value.absolute())

    config_file.write_text(json.dumps(initial_config_dict, indent=4))
    synced_config_settings = safely_get_settings().model_dump_json(indent=4)
    config_file.write_text(synced_config_settings)

def _start_server(port: int, host: str):
    """Start the HTTP service."""
    from locknessie.server import app
    uvicorn.run(app, host=host, port=port)

def _stop_server(pid: int, sig: int):
    """Stop the HTTP service."""
    os.kill(pid, sig)


@click.group()
def cli():
    """Lock Nessie CLI"""

@cli.group()
def config():
    """Configure Lock Nessie settings."""

@config.command()
def init():
    """Initialize a new config file"""
    config_dict = {}
    config_path = get_config_path()
    if config_path.exists():
        click.echo(f"Config file already exists at {config_path}")
        return
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config_dict["config_path"] = config_path
    config_dict["config_dir"] = config_path.parent
    config_dict["openid_issuer"] = click.prompt("Which OpenID provider are you using?", type=click.Choice([v.value for v in OpenIDIssuer]))
    match config_dict["openid_issuer"]:
        case OpenIDIssuer.microsoft:
            config_dict["openid_client_id"] = click.prompt("What is your Microsoft client ID?", type=str)
            if click.prompt("Do you want to set daemon auth? (y/n)", type=click.Choice(["y", "n"])) == "y":
                config_dict["openid_secret"] = click.prompt("What is your Microsoft Application secret?", type=str)
                config_dict["openid_tenant"] = click.prompt("What is your Microsoft tenant ID?", type=str)
        case _:
            click.secho("That provider is not supported yet", fg="red", err=True)
            return
    _ = _sync_config_settings(config_dict, config_path)
    click.echo(f"Config file initialized at {config_path}.")

def catch_noconfigerror(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except NoConfigError as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            return
    return wrapper

def catch_invalid_config(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            error_list = e.errors()
            if error_list:
                click.secho("Invalid or missing config values:", fg="red", err=True)
                for err in error_list:
                    loc = ".".join(str(x) for x in err.get("loc", []))
                    msg = err.get("msg", "Unknown error")
                    click.secho(f"  - {loc}: {msg}", fg="yellow", err=True)
                click.echo("If using the CLI or browser auth, please run `locknessie config init` to initialize the config file.")
            else:
                click.secho(f"Error: {e}", fg="red", err=True)
    return wrapper

@config.command()
@click.argument("key")
@click.argument("value")
@catch_noconfigerror
def set(key: str, value: str):
    """Set a config value"""
    config_settings = safely_get_settings()
    try:
        setattr(config_settings, key, value)
    except AttributeError:
        click.echo(f"Invalid config key: {key}")
        return
    _ = _sync_config_settings(config_settings.model_dump(), config_settings.config_path)
    click.echo(f"Config file updated at {config_settings.config_path}.")


@cli.group()
@add_config_options
@click.pass_context
def service(ctx, **kwargs):
    """Manage the Lock Nessie HTTP service."""
    ctx.obj = _filter_none_kwargs(kwargs)
    raise NotImplementedError(("Service will allow polling to auth tools like Dremio. "
                              "Sevice implementation is not yet complete, stay tuned!"))

@service.command()
@click.option("--daemon", is_flag=True, help="Run the HTTP service as a daemon")
@click.pass_context
@catch_noconfigerror
def start(ctx, daemon):
    """Start the HTTP service."""
    config_kwargs = ctx.obj or {}
    config_settings = ConfigSettings(**config_kwargs)
    port = config_settings.auth_callback_port
    host = config_settings.auth_callback_host
    if daemon:
        process = multiprocessing.Process(target=_start_server, args=(port, host))
        pid = process.start()
        pid_cache = config_settings.config_path / "pid"
        pid_cache.write_text(str(pid))
        click.echo(f"HTTP service started on {host}:{port} with PID {pid}")
    else:
        _start_server(port, host)

@service.command()
@click.option("--kill", is_flag=True, help="Send a SIGKILL signal to the HTTP service. Useful if the server refuses to stop.")
@click.pass_context
@catch_noconfigerror
def stop(ctx, kill: bool):
    """Stop the HTTP service."""
    config_kwargs = ctx.obj or {}
    config_settings = ConfigSettings(**config_kwargs)
    sig_enum = "SIGKILL" if kill else "SIGINT"
    sig = getattr(signal, sig_enum)
    pid_cache = config_settings.config_path / "pid"
    if not pid_cache.exists():
        click.echo("HTTP service is not running")
        return
    pid = int(pid_cache.read_text())
    click.echo(f"Terminating HTTP service with PID {pid} with signal {sig_enum}")
    _stop_server(pid, sig)
    click.echo(f"HTTP service {sig_enum} stop signal sent")

@cli.group()
@add_config_options
@click.pass_context
def token(ctx, **kwargs):
    """Manage OpenID tokens."""
    ctx.obj = _filter_none_kwargs(kwargs)

@token.command()
@click.pass_context
@catch_noconfigerror
@catch_invalid_config
def show(ctx):
    """Show the active OpenID bearer token."""
    from locknessie.main import LockNessie
    config_kwargs = ctx.obj or {}
    settings = safely_get_settings(**config_kwargs)
    import locknessie.settings as settings_mod
    settings_mod.settings = settings
    token = LockNessie().get_token()
    click.echo(token)


