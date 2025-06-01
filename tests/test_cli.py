import os
import json
import tempfile
import shutil
import pytest
from click.testing import CliRunner
from locknessie.cli import cli
from locknessie.settings import get_config_path, ConfigSettings

@pytest.fixture
def temp_config_dir(monkeypatch):
    # Create a temporary directory for config
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, "config.json")
    monkeypatch.setenv("LOCKNESSIE_CONFIG_PATH", config_path)
    yield config_path
    shutil.rmtree(temp_dir)

def test_config_init_and_set_microsoft_daemon(temp_config_dir, monkeypatch):
    runner = CliRunner()
    # Simulate interactive prompts for Microsoft with daemon auth
    inputs = [
        "microsoft",  # OpenID provider
        "123456-microsoft-client-id",  # client ID
        "y",  # set daemon auth
        "super-secret",  # secret
        "tenant-abc",  # tenant
    ]
    result = runner.invoke(cli, ["config", "init"], input="\n".join(inputs) + "\n")
    assert result.exit_code == 0
    assert "Config file initialized" in result.output
    # Check config file contents
    with open(temp_config_dir) as f:
        config = json.load(f)
    assert config["openid_issuer"] == "microsoft"
    assert config["openid_client_id"] == "123456-microsoft-client-id"
    assert config["openid_secret"] == "super-secret"
    assert config["openid_tenant"] == "tenant-abc"
    # Now test setting a config value
    result2 = runner.invoke(cli, ["config", "set", "openid_client_id", "new-client-id"])
    assert result2.exit_code == 0
    assert "Config file updated" in result2.output
    with open(temp_config_dir) as f:
        config2 = json.load(f)
    assert config2["openid_client_id"] == "new-client-id"
