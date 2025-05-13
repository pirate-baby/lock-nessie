# Lock Nessie

Quickly and simply add OpenID auth to your Iceberg Nessie stack


# Server
This component facilitiates your OpenID Oauth2 login flow.

### Envars:
Required for all providers:
- `LOCKNESSIE_ENVIRONMENT`: 'production' for released code, 'development' for local development
- `LOCKNESSIE_REDIRECT_BASE`: The base URL for redirects
- `LOCKNESSIE_OPENID_ISSUER`: The issuer of the OpenID client, one of:
    - `microsoft` # entra
    - `keycloak`
- `LOCKNESSIE_OPENID_CLIENT_ID`: The client ID of the OpenID client
- `LOCKNESSIE_OPENID_CLIENT_SECRET`: The client secret of the OpenID client
- `LOCKNESSIE_SECRET_PROVIDER`: The provider where the secret is stored, one of:
    - `aws_secrets_manager`
    - `hachicorp_vault`

Required for `microsoft`:
- `LOCKNESSIE_OPENID_TENANT`: The tenant of the OpenID client (required for Microsoft)

Required for `keycloak`:
- `LOCKNESSIE_OPENID_REALM`: The realm of the OpenID client (required for Keycloak)
- `LOCKNESSIE_OPENID_URL`: The URL of the OpenID provider

Required for `aws`:
_note_: lock-nessie uses the standard [boto3 credentials order](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html). For lock-nessie to leverage AWS Secrets Manager, credentials must be provided that have:
```
    "secretsmanager:CreateSecret",       // Create a new secret
    "secretsmanager:GetSecretValue",     // Read the secret value
    "secretsmanager:DescribeSecret",     // Read secret metadata
    "secretsmanager:PutSecretValue"      // Write/update secret value
```

Optional:
- `LOCKNESSIE_MAX_AGE`: The maximum age of the cookie in seconds (default: 31536000 - 1 year). Note this is _not_ the same as the token age for the OpenID auth.

## Client:
Required for all providers:
- `LOCKNESSIE_SECRET_PROVIDER`: The provider where the secret is stored, one of:
    - `aws_secrets_manager`
    - `hachicorp_vault`
- `LOCKNESSIE_SECRET_IDENTIFIER`: The resource id for the secret, like an arn in aws.

Optional:
- `LOCKNESSIE_CACHE_PATH`: Where to store the cached OpenID token.
- `LOCKNESSIE_SERVER_URL`: If provided, the client will attempt to pop open a login window when the token has expired.

## Client integrations

**PyIceberg**
```python

from locknessie.client.pyiceberg import load_catalog

catalog = load_catalog("nessie", uri="http://nessie:19120/iceberg/main/")
```
*note:* There is a bunch of auth bits in pyiceberg that indicate better integration may be possible, but it is non-obvious how a web-based login flow, refresh token etc would work in practice. TODO see if this can be refined.