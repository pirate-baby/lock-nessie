# Lock Nessie

<div align="center">
    <img src="src/server/static/logo.png" width="300" alt="logo"/>
</div>

_Quickly and simply add OpenID auth to your Iceberg Nessie stack._

# Installation
- `pip install locknessie`
- `uv add locknessie`

Or use the docker image (primarily intended for server):
```bash
docker run --rm --env-file .env -p 8080:8080 ghcr.io/pirate-baby/lock-nessie:latest # starts the server at http://localhost:8080
```

OpenID auth requires a server that can facilitiate the login flow, and a client that can store (and re-request as needed) the resulting bearer token
once that flow has been completed. `lock-nessie` provides both of those for nessie-compatible Iceberg REST clients.

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

### Modifying the home template
The `home.html` template is used for the root path ("/") for both authed and unauthed users. It is a standard Jinja2 template with the following context variables passed to it:

- `request`: The FastAPI request object, where login cookies have been assigned.
- `user`: The username of the logged-in user (None if not logged in)
- `is_logged_in`: Boolean indicating if a user is logged in
- `expires`: Datetime object of when the session expires (None if not logged in)
- `time_until_expiry`: Human-readable string of time until session expires (None if not logged in)
- `aws_secret_arn`: Optional AWS secret ARN if provided as a `get` param (from a successful login)

You can create a different template that matches your company/use case and set `LOCKNESSIE_TEMPLATES_DIR_PATH` to override the location.

>![WARNING]
> The template file must be named `home.html` to override the default template.

# Client:
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