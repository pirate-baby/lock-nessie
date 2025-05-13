from typing import Optional, Type, TYPE_CHECKING
from fastapi import APIRouter, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from datetime import datetime
from common.logger import get_logger
from server.settings import settings, OpenIDIssuer, SecretProvider

if TYPE_CHECKING:
    from server.auth.base import AuthBase
    from server.secret.base import SecretBase

logger = get_logger(__name__)

router = APIRouter(prefix="/auth")

def get_provider() -> Type["AuthBase"]:
    """determine provider from settings and return the appropriate class"""
    match settings.openid_issuer:
        case OpenIDIssuer.microsoft:
            from server.auth.microsoft import MicrosoftAuth
            return MicrosoftAuth()
        case OpenIDIssuer.keycloak:
            from server.auth.keycloak import KeycloakAuth
            return KeycloakAuth()
        case _:
            raise ValueError(f"Unsupported OpenID issuer: {settings.openid_issuer}")

def get_secret(name: str) -> Type["SecretBase"]:
    """determine secret provider from settings and return the appropriate class"""
    match settings.secret_provider:
        case SecretProvider.aws_secrets_manager:
            from server.secret.aws_secrets_manager import AWSSecretsManagerSecret
            return AWSSecretsManagerSecret(name)
        case _:
            raise ValueError(f"Unsupported Secret Provider: {settings.secret_provider}")

def set_auth_cookie(response: Response, key: str, value: str, secure: bool = True):
    """Helper function to set authentication cookies with consistent settings"""
    logger.info(f"Setting cookie: {key}")
    response.set_cookie(
        key=key,
        value=value,
        httponly=secure,
        secure=secure,
        samesite="lax",
        max_age=settings.max_age,
    )

def set_auth_cookies(response: Response,
                     user: str,
                     token: str,
                     refresh: str,
                     expires: int)->None:
    """set the authentication cookies"""
    logger.info("Setting authentication cookies")
    set_auth_cookie(response, "id_token", token)
    set_auth_cookie(response, "refresh_token", refresh)
    set_auth_cookie(response, "user", user)
    set_auth_cookie(response, "openid_expires", expires)
    logger.info("All cookies set successfully")

def delete_auth_cookies(response: Response)->None:
    """delete the authentication cookies"""
    logger.info("Deleting authentication cookies")
    response.delete_cookie("id_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("user")
    response.delete_cookie("openid_expires")
    logger.info("All cookies deleted successfully")




@router.get("/login")
async def login():
    """Log in via the OpenID provider"""
    provider = get_provider()
    return RedirectResponse(url=provider.get_auth_url())

@router.get("/callback")
async def auth_callback(code: Optional[str] = None,
                        error: Optional[str] = None):
    """Handle the callback from the OpenID provider"""
    logger.info("Processing auth callback...")
    if error:
        logger.error(f"Auth error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {error}",
        )
    if not code:
        logger.error("No authorization code provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No authorization code provided",
        )
    provider = get_provider()

    result = provider.exchange_code_for_token(code)
    if "error" in result:
        error_description = result.get(
            "error_description", "No error description available"
        )
        logger.error(
            f"Token acquisition failed - Error: {result['error']}, Description: {error_description}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token acquisition failed: {result['error']} - {error_description}",
        )
    user = result["id_token_claims"]["preferred_username"]
    token = result["id_token"]
    refresh = result["refresh_token"]
    expires = result["id_token_claims"]["exp"]

    secret = get_secret(user)
    secret_identifier = "=".join(secret.secret_identity_pair)
    response = RedirectResponse(url=f"/?{secret_identifier}", status_code=status.HTTP_303_SEE_OTHER)
    secret.set_token_value(token)
    set_auth_cookies(response, user, token, refresh, expires)
    logger.info("Redirecting to home page")
    return response


@router.get("/logout")
async def logout(request: Request,
                 response: Response):
    """Log out the user"""
    user = request.cookies.get("user")
    logger.info(f"Logging out user {user}")
    secret = get_secret(user)
    secret.delete_token_value()
    response = RedirectResponse(
        url="/", status_code=status.HTTP_303_SEE_OTHER
    )
    delete_auth_cookies(response)
    return response


