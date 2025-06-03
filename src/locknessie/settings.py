from enum import Enum
from pathlib import Path
import os
from typing import Union, Optional, Type
from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, JsonConfigSettingsSource, InitSettingsSource, SettingsConfigDict
from typing import Optional

from locknessie.logger import get_logger

logger = get_logger(__name__)

class NoConfigError(Exception):
    """exception raised when no config file is found"""
    pass

class Environment(str, Enum):
    release = "release" # code that is read-only and published in a release
    development = "development" # code that is being actively developed
    production = "release" # legacy value for backwards compatibility

    def __eq__(self, other):
        """legacy support for the value `production` which is confusing to users"""
        if isinstance(other, str):
            if self is Environment.release and other == "production":
                return True
            return str(self.value) == other
        if isinstance(other, Environment):
            return str(self.value) == str(other.value)
        return NotImplemented

class OpenIDIssuer(str, Enum):
    microsoft = "microsoft"
    keycloak = "keycloak"

def get_config_path(config_path: Optional[Union[Path, str]] = None) -> Path:
    """gets the config _json file_ full path"""
    if config_path:
        logger.debug(f"Using config path from CLI: {config_path}")
        config_path = Path(config_path)

    elif from_env := os.getenv("LOCKNESSIE_CONFIG_PATH"):
        logger.debug(f"Using config path from env: {from_env}")
        config_path = Path(from_env)
    else:
        logger.debug("Using default config path: ~/.locknessie/config.json")
        config_path = Path.home() / ".locknessie" / "config.json"
    assert not config_path.is_dir(), "Config path must be a file, not a directory"
    assert config_path.suffix == ".json", "Config path must be a JSON file"
    return config_path



class ConfigSettings(BaseSettings):
    """settings derived from the cli, envars, and config file"""

    model_config = SettingsConfigDict(
        json_file_encoding="utf-8",
        env_prefix="locknessie_",
        case_sensitive=False
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: InitSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Precedence: CLI/init > env > config file
        return (
            init_settings,  # CLI args
            env_settings,   # Environment variables
            JsonConfigSettingsSource(settings_cls, init_settings.init_kwargs["config_path"]),  # recursively load config file
        )

    config_path: Path
    config_dir: Path = Field(..., description="The directory for the config file")
    environment: Environment = Field(Environment.release, description="'release' for released code, 'development' for local development")
    openid_issuer: OpenIDIssuer = Field(..., description="The issuer of the OpenID client")
    openid_client_id: str = Field(..., description="The client ID of the OpenID client")
    openid_tenant: Optional[str] = Field(None, description="The tenant of the OpenID client")
    openid_allow_all_tenants: bool = Field(True, description="Whether to allow all tenants to be used for OpenID auth")
    openid_secret: Optional[str] = Field(None, description="The secret of the OpenID client, used for daemon auth")
    openid_realm: Optional[str] = Field(None, description="The realm of the OpenID client")
    openid_url: Optional[str] = Field(None, description="The URL of the OpenID provider")

    # Secret settings
    secret_name: str = Field("token", description="The name of the secret to be retrieved")

    # port settings
    auth_callback_port: Optional[int] = Field(default=1234, description="The port for the OpenID auth callback server")
    impersonation_port: Optional[int] = Field(default=8200, description="The port for the vault impersonation server")
    auth_callback_host: Optional[str] = Field(default="0.0.0.0", description="The host for the OpenID auth callback server")

    @model_validator(mode="before")
    def set_config_dir_from_path(cls, values):
        if values.get("config_path") and not values.get("config_dir"):
            values["config_dir"] = Path(values["config_path"]).parent
        return values

    @model_validator(mode="before")
    def normalize_environment(cls, values):
        env = values.get("environment")
        if env == "production":
            values["environment"] = "release"
        return values

def safely_get_settings(config_path: Optional[Union[Path, str]] = None,
                        **kwargs) -> Type["BaseSettings"]:
    """safely get the settings and direct the user to init the config if needed
    """
    if config_path:
        try:
            assert config_path.exists()
        except AssertionError as e:
            raise NoConfigError(
                f"Config file not found at {config_path}. Please run `locknessie config init` to initialize the config file."
            ) from e

    config_path = get_config_path(config_path)
    return ConfigSettings(config_path=config_path, **kwargs)

