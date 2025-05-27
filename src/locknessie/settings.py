from enum import Enum
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, JsonConfigSettingsSource
from typing import Optional


class NoConfigError(Exception):
    """exception raised when no config file is found"""
    pass

class OpenIDIssuer(str, Enum):
    microsoft = "microsoft"
    keycloak = "keycloak"

class EnvSettings(BaseSettings):
    """core settings derived from environment variables"""
    model_config = SettingsConfigDict(env_prefix="locknessie_", case_sensitive=False)
    environment: str = Field(..., description="'production' for released code, 'development' for local development")
    config_path: Path = Field(description="The parent path for all config and auth cache storages",
                                  default=Path.home() / ".locknessie")

class ConfigSettings(BaseSettings):
    """settings derived from the config file"""
    model_config = SettingsConfigDict(json_file=EnvSettings().config_path / "config.json", json_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (JsonConfigSettingsSource(settings_cls),)


    env: EnvSettings = Field(default_factory=EnvSettings)

    openid_issuer: OpenIDIssuer = Field(..., description="The issuer of the OpenID client")
    openid_client_id: str = Field(..., description="The client ID of the OpenID client")
    openid_tenant: Optional[str] = Field(None, description="The tenant of the OpenID client")
    openid_realm: Optional[str] = Field(None, description="The realm of the OpenID client")
    openid_url: Optional[str] = Field(None, description="The URL of the OpenID provider")

    # Secret settings
    secret_name: str = Field("token", description="The name of the secret to be retrieved")

    # port settings
    auth_callback_port: Optional[int] = Field(default=1234, description="The port for the OpenID auth callback server")
    impersonation_port: Optional[int] = Field(default=8200, description="The port for the vault impersonation server")

def safely_get_settings() -> ConfigSettings:
    """safely get the settings and direct the user to init the config if needed"""
    env_settings = EnvSettings()
    if not env_settings.config_path.exists():
        raise NoConfigError(
        "It looks like you do not have a config file initialized yet. "
        "Please run `locknessie config init` to initialize the config file. "
        f"(expected config file at: {env_settings.config_path / 'config.json'})"
    )
    return ConfigSettings()