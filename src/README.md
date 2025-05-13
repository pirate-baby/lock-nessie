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

Optional:
- `LOCKNESSIE_MAX_AGE`: The maximum age of the cookie in seconds (default: 31536000 - 1 year). Note this is _not_ the same as the token age for the OpenID auth.

