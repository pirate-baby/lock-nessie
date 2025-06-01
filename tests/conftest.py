import pytest
from locknessie.settings import ConfigSettings, get_config_path
import yaml
import os
import json

def _build_config_from_param(request):
    try:
        provider, user_type, overrides = request.param
    except ValueError:
        provider, user_type = request.param
        overrides = {}

    with open("/app/tests/test_secrets.yml") as f:
        secrets = yaml.safe_load(f)["secrets"][provider][user_type]
    assert secrets, f"No secrets found for {provider} {user_type}"

    config = {
        "openid_issuer": provider,
        "secret_name": "token",
        "auth_callback_port": 1234,
        "impersonation_port": 8200,
    }
    config.update(secrets)
    config.update(overrides)
    return provider, user_type, overrides, config

@pytest.fixture(scope="function")
def patched_settings(request):
    provider, user_type, overrides, config = _build_config_from_param(request)
    return provider, user_type, overrides, ConfigSettings(config_path=get_config_path(), **config)

@pytest.fixture(scope="function")
def patched_settings_file(tmp_path, request):
    provider, user_type, overrides, config = _build_config_from_param(request)
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    return provider, user_type, overrides, str(config_path)
