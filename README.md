# Lock Nessie

<div align="center">
    <img src="src/server/static/logo.png" width="300" alt="logo"/>
</div>

_Quickly and simply add OpenID auth to your Iceberg Nessie tools._

OpenID auth requires a flow to facilitiate the login to get access and refresh tokens, a way to distribute that access token to the services that need it (such as your Juypter notebook code, Dremio instance etc), and a process to automatically refresh the token when it exipires. This process is what `locknessie` does.

# Installation
- `pip install locknessie[<provider>]`
- `uv add locknessie[<provider>]`

You'll need to install the provider required for Nessie authentication - such as `microsoft` if your Nessie uses Microsoft Entra OpenID for auth, `keycloak` etc.

There is also a docker image:
```bash
docker run --rm --env-file .env -p 8080:8080 ghcr.io/pirate-baby/locknessie:microsoft-latest
```

`locknessie` has both CLI and module components, and they can be used in conjunction with one another.

## CLI

for a list of commands and help text run

```bash
> locknessie --help
```
When you first install `locknessie` you need to run `locknessie config init` to set up the configuration. Locknessie will ask you for information required for your provider and store it in a config file (located by default at `~/.locknessie/config.json`). You can manually edit any of the settings there, or use `locknessie config set <setting> <setting-value>`.

Once configured, you can initialize auth and get a bearer token with `locknessie token show`. If this is your first time logging in, a browser window will open automatically for you to authorize with the provider (microsoft, google, keycloak etc). **Note**: if you are running in a browserless environment (such as a docker container) then locknessie will print the login URL into the console logs where you can copy it from and paste into your browser of choice. Once you have aproved the auth, locknessie will print the bearer token into the logs - this token can now be used in your Nessie requests.

If you run `locknessie token show` again, you will see it returns the same token (or a new one once that token expires) without opening a browser window. The token refresh cycle is now in place, and locknessie will use a refresh token behind the scenes to always return you a valid token.

## Module

Typically you will need to access this bearer token in code. Once `locknessie` has been initialized with your authentication you can easily access the tokens via module:

```python

from locknessie.main import LockNessie
from pyiceberg.catalog import load_catalog

# this will return a new valid token, refreshed if needed.
token = LockNessie().get_token()

catalog = load_catalog(
    "nessie",
    uri= "https://your-nessie-instance.com/iceberg/main/",
    token=token
)

namespaces = catalog.list_namespaces()
```

## Hashicorp Vault impersonation
Dremio (and possibly other tools) will source an auth token from a Hashicorp Vault secret; for local use, `locknessie` exposes an API endpoint that will mimic vault and allow Dremio to authenticate using your existing OpenID token. Once you have initialized the token exchange, run `locknessie service start -d` to spin up the endpoint. When you are done with the endpoint, you can spin it down with `locknessie service stop`. The default host for the vault endpoint will be `http://localhost:8200`.

### Envars:
Required for all providers:
- `LOCKNESSIE_OPENID_ISSUER`: The issuer of the OpenID client, one of:
    - `microsoft` # entra
    - `keycloak`

- `LOCKNESSIE_OPENID_CLIENT_ID`: The client ID of the OpenID client

Required for `microsoft`:
- `LOCKNESSIE_OPENID_CLIENT_ID`: The tenant of the OpenID client (required for Microsoft)

Required for `keycloak`:
- `LOCKNESSIE_OPENID_REALM`: The realm of the OpenID client (required for Keycloak)
- `LOCKNESSIE_OPENID_URL`: The URL of the OpenID provider

## Client integrations

## Hashicorp Vault impersonation


## Dremio