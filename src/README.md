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

