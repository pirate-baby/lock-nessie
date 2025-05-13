from server.secret.base import SecretBase
import boto3

class AWSSecretsManagerSecret(SecretBase):

    def __init__(self, user: str):
        super().__init__(user)
        self.client = boto3.client("secretsmanager")
        self.secret_arn = self.create_secret()

    def set_token_value(self, token: str) -> None:
        """set the token value in the secret store"""
        self.create_secret()
        self.logger.info(f"Setting token value for {self.user}")
        result = self.client.put_secret_value(
            SecretId=self.secret_name,
            SecretString=token,
        )
        if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise Exception(f"Failed to set token value for {self.user}: {result}")
        self.logger.info(f"Token value set for {self.user}")

    def delete_token_value(self):
        """delete the token value from the secret store"""
        self.logger.info(f"Setting empty token value for {self.user}")
        self.create_secret()
        self.set_token_value(self.deleted_string)


    def create_secret(self) -> str:
        """create the empty secret if it doesn't already exist, and return the secret arn"""
        self.logger.info(f"Creating secret for {self.user}")
        try:
            secret = self.client.create_secret(
                Name=self.secret_name,
                SecretString=self.deleted_string,
            )
        except self.client.exceptions.ResourceExistsException:
            self.logger.info(f"Secret already exists for {self.user}, skipping creation")
            secret = self.client.describe_secret(SecretId=self.secret_name)
        except Exception as e:
            self.logger.error(f"Error creating secret for {self.user}: {e}")
            raise e
        return secret["ARN"]

    @property
    def secret_identity_pair(self) -> tuple[str, str]:
        """get the secret arn"""
        return "aws_secret_arn", self.secret_arn