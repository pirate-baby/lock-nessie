# Lock Nessie

**Easily integrate OpenID authentication and authorization into your Apache Nessie and Iceberg projects.**

Lock Nessie is a drop-in tool that handles OpenID RBAC for you, so you don't have to roll your own. It works for both interactive users (scripts, Jupyter notebooks) and service accounts (ETL, headless/daemon jobs), making it simple to get and refresh tokens for your Nessie metadata server.

---

## Features

- **Drop-in OpenID Auth for Nessie/Iceberg**: No need to implement RBAC yourself.
- **CLI and Python Module**: Use from the command line or directly in your code.
- **Supports User and Daemon Auth**: Interactive browser login or headless service account flows.
- **Easy Configuration**: One-time setup, then use everywhere.

---

## Installation

You can install Lock Nessie using either `pip` or [`uv`](https://github.com/astral-sh/uv):

```bash
# With pip
pip install locknessie[microsoft]

# Or with uv (faster alternative to pip)
uv pip install locknessie[microsoft]

# For other providers in the future
# pip install locknessie[keycloak]
# uv pip install locknessie[keycloak]
```

---

## Quickstart

### 1. Configure Lock Nessie

Run the following to set up your config file (by default at `~/.locknessie/config.json`):

```bash
locknessie config init
```

You'll be prompted for your OpenID provider and credentials (e.g., Microsoft client ID, secret & tenant for daemon auth).

You can update settings later if needed:

```bash
locknessie config set <key> <value>
```

or by editing the file directly.

---

### 2. Get a Token (CLI)

Get a valid OpenID bearer token for your Nessie server:

```bash
locknessie token show
```

- The first time, you'll be prompted to log in via browser (for user auth).
- For daemon/service accounts, set up your secret and tenant during config.

This is all the setup you need. The refresh token is stored locally, and the cycle can now run as long as the provider's refresh token is valid. When the refresh token expires you will be prompted to log in via browser again.

> [!Note]
> If you are running locknessie in a container, the url for the browser login will be
> printed into the container logs. Make sure the auth_callback_port is exposed or locknessie will not be able to complete the auth flow and log you in.

---

### 3. Use in Python Scripts

```python
from locknessie.main import LockNessie

# Get a valid token (auto-refreshes as needed)
token = LockNessie().get_token()

# Use with your Nessie/Iceberg client
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "nessie",
    uri="https://your-nessie-instance.com/iceberg/main/",
    token=token
)
```

---

### 4. Headless/Daemon Auth

To use Lock Nessie in headless or daemon mode (for service accounts, ETL jobs, CI/CD, etc.), you **must provide an OpenID secret** from your authentication provider (such as Microsoft or Keycloak). This secret is required for non-interactive authentication and can be set in any of the following ways:

- **CLI**: During `locknessie config init` or with `locknessie config set openid_secret <your-secret>`
- **Config file**: Add `"openid_secret": "<your-secret>"` to your config JSON
- **Environment variable**: Set `LOCKNESSIE_OPENID_SECRET=<your-secret>`

You will also need to provide any other required settings for your provider (e.g., `LOCKNESSIE_OPENID_TENANT` for Microsoft).

Once configured, you can use the CLI or Python module as shown above, and Lock Nessie will use the daemon/service account flow to obtain tokens without requiring browser interaction.

---

## Configuration & Environment Variables

You can set any Lock Nessie configuration value in **three ways**:

1. **CLI Argument**: Pass as a command-line argument (e.g., `--auth-callback-port 4321`).
2. **Environment Variable**: Set with the `LOCKNESSIE_` prefix (e.g., `LOCKNESSIE_AUTH_CALLBACK_PORT=4321`).
3. **Config File**: Edit the config file directly (default: `~/.locknessie/config.json`) or use the CLI tool (e.g., `locknessie config set auth_callback_port 4321`).

**Order of evaluation (highest priority first):**

1. CLI argument (e.g., `locknessie token show --auth-callback-port 4321`)
2. Environment variable (e.g., `LOCKNESSIE_AUTH_CALLBACK_PORT=4321 locknessie token show`)
3. Config file (manually edit or use `locknessie config set`)

All config values can be set using any of these methods, and Lock Nessie will use the highest-priority value found.

**Required for all providers:**

- `LOCKNESSIE_OPENID_ISSUER`: The OpenID provider (`microsoft`, `keycloak`)
- `LOCKNESSIE_OPENID_CLIENT_ID`: The client/application ID

**Microsoft-specific:**

- `LOCKNESSIE_OPENID_TENANT`: Tenant ID (required for daemon/service auth)
- `LOCKNESSIE_OPENID_SECRET`: Application secret (required for daemon/service auth)

**Keycloak (future):**

- `LOCKNESSIE_OPENID_REALM`: Keycloak realm
- `LOCKNESSIE_OPENID_URL`: Keycloak server URL

**Other settings:**

- `LOCKNESSIE_CONFIG_PATH`: Path to config file (default: `~/.locknessie/config.json`)
- `LOCKNESSIE_AUTH_CALLBACK_PORT`: Port for browser-based auth (default: 1234)
- `LOCKNESSIE_IMPERSONATION_PORT`: Port for Vault impersonation service (default: 8200)
- `LOCKNESSIE_AUTH_CALLBACK_HOST`: Host for callback server (default: `0.0.0.0`)

---

## CLI Reference

- `locknessie config init` — Initialize config file
- `locknessie config set <key> <value>` — Set a config value
- `locknessie token show` — Print a valid OpenID token

---

## Use Cases

- **Jupyter notebooks**: Authenticate and use Nessie/Iceberg with one line.
- **ETL/Service jobs**: Headless daemon/service account auth with environment variables.

---

## Provider Support

- **Microsoft Entra/Azure AD**: Supported (user and daemon/service flows)
- **Keycloak**: Coming soon

---

## Contributing

PRs and issues welcome!

---

## License

MIT