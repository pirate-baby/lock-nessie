from typing import Optional
import boto3
import webbrowser
from client.settings import settings, ExpiredAction
from client.secret.base import SecretBase, ExpiredTokenError

class AWSSecretsManagerSecret(SecretBase):
    client: "boto3.client"

    def __init__(self,
                 secret_identifier: Optional[str] = None):
        super().__init__(secret_identifier)
        self.client = boto3.client("secretsmanager")


    def retrieve_token(self) -> Optional[str]:
        secret = self.client.get_secret_value(SecretId=self.secret_identifier)
        value = secret["SecretString"]
        if not (value == settings.deleted_string):
            return value
        if settings.server_url:
            webbrowser.open(f"{settings.server_url}/auth/login")
        raise ExpiredTokenError("Token expired, please login to the auth server to continue")