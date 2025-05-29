import pytest
import yaml
import os
import json
from unittest.mock import patch
from src.locknessie.settings import safely_get_settings, OpenIDIssuer

@pytest.fixture(scope="function")
def patched_settings(tmp_path, request):
    provider, user_type = request.param

    config_dir = tmp_path / ".locknessie"
    config_dir.mkdir(parents=True, exist_ok=True)
    os.environ["LOCKNESSIE_CONFIG_PATH"] = str(config_dir)

    with open("/app/tests/test_secrets.yml") as f:
        secrets = yaml.safe_load(f)["secrets"][provider][user_type]

    config = {
        "openid_issuer": provider,
        "openid_client_id": secrets["openid_client_id"],
        "openid_tenant": secrets["openid_tenant"],
        "openid_secret": secrets.get("openid_secret", None),
        "openid_realm": secrets.get("openid_realm", None),
        "openid_url": secrets.get("openid_url", None),
        "secret_name": "token",
        "auth_callback_port": 1234,
        "impersonation_port": 8200,
    }
    config_path = config_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)

    # patch in the module under test
    patch_target = f"locknessie.auth_providers.{provider}.safely_get_settings"
    with patch(patch_target, safely_get_settings):
        yield provider, user_type, str(config_dir)
    del os.environ["LOCKNESSIE_CONFIG_PATH"]