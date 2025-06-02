import json
import pytest
from locknessie.settings import safely_get_settings, NoConfigError


class TestSettings:

    def test_all_envars(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.json"
        monkeypatch.setenv("LOCKNESSIE_CONFIG_PATH", str(config_path))
        monkeypatch.setenv("LOCKNESSIE_OPENID_ISSUER", "microsoft")
        monkeypatch.setenv("LOCKNESSIE_OPENID_CLIENT_ID", "1234567890")
        monkeypatch.setenv("LOCKNESSIE_OPENID_TENANT", "1234567890")
        monkeypatch.setenv("LOCKNESSIE_OPENID_SECRET", "1234567890")
        settings = safely_get_settings()
        assert settings.config_path == config_path
        assert settings.openid_issuer == "microsoft"
        assert settings.openid_client_id == "1234567890"
        assert settings.openid_tenant == "1234567890"
        assert settings.openid_secret == "1234567890"

    def test_config_file(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({
            "openid_issuer": "microsoft",
            "openid_client_id": "1234567890",
            "openid_tenant": "1234567890",
            "openid_secret": "1234567890",
        }))
        settings = safely_get_settings(config_path=config_path)
        assert settings.config_path == config_path
        assert settings.openid_issuer == "microsoft"
        assert settings.openid_client_id == "1234567890"
        assert settings.openid_tenant == "1234567890"
        assert settings.openid_secret == "1234567890"

    def test_via_kwargs(self, tmp_path, monkeypatch):
        settings = safely_get_settings(openid_issuer="keycloak",
                                       openid_client_id="1234567890",
                                       openid_tenant="1234567890",
                                       openid_secret="1234567890")
        assert settings.openid_issuer == "keycloak"
        assert settings.openid_client_id == "1234567890"
        assert settings.openid_tenant == "1234567890"
        assert settings.openid_secret == "1234567890"

    def test_all_sources(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({
            "openid_issuer": "microsoft",
            "openid_client_id": "1234567890",
            "openid_tenant": "1234567890",
            "openid_secret": "1234567890",
        }))
        monkeypatch.setenv("LOCKNESSIE_OPENID_ISSUER", "keycloak")
        settings = safely_get_settings(config_path=config_path, openid_tenant="54321")
        assert settings.openid_issuer == "keycloak"
        assert settings.openid_client_id == "1234567890"
        assert settings.openid_tenant == "54321"
        assert settings.openid_secret == "1234567890"

    def test_no_config_file(self, tmp_path):
        with pytest.raises(NoConfigError):
            safely_get_settings(config_path=tmp_path / "config.json")