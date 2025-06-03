from pytest import mark as m
import re
from pathlib import Path
import importlib
import sys
import time
import subprocess
import textwrap
import os
from locknessie.settings import safely_get_settings

login_url_regex = {
    "microsoft": r"https://login.microsoftonline.com/common/oauth2\S+",
}

@m.describe("When getting a token")
class TestProviders:

    @m.parametrize(
        "patched_settings_file",
        [("microsoft", "user", {"openid_allow_all_tenants": True})],
        indirect=True
    )
    @m.context("and the user flow is selected")
    @m.context("and no cache exists")
    @m.it("tests that the login URL is printed to stdout")
    def test_get_token_user_no_cache(self, patched_settings_file):
        provider, user_type, _, config_path = patched_settings_file
        provider_class = f"{provider.capitalize()}Auth"

        # Script to run in subprocess
        script = textwrap.dedent(f'''
            import importlib
            from pathlib import Path
            from locknessie.settings import safely_get_settings
            from locknessie.auth_providers.{provider} import {provider_class}
            settings = safely_get_settings(config_path=Path("{config_path}"))
            auth = {provider_class}(auth_type="{user_type}", settings=settings)
            auth.get_token()
        ''')

        env = os.environ.copy()
        env["LOCKNESSIE_CONFIG_PATH"] = config_path

        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        try:
            time.sleep(2)
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        finally:
            out, err = proc.communicate()
        assert re.search(login_url_regex[provider], " ".join((out,err,))), "No login URL printed to stdout"

    @m.parametrize(
        "patched_settings_file",
        [("microsoft", "daemon")],
        indirect=True
    )
    @m.context("and the daemon flow is selected")
    @m.it("tests that the token is returned without a cache")
    def test_get_token_daemon(self, patched_settings_file, monkeypatch):
        provider, user_type, _, config_path = patched_settings_file
        provider_class = f"{provider.capitalize()}Auth"
        monkeypatch.setenv("LOCKNESSIE_CONFIG_PATH", config_path)
        module_path = f"locknessie.auth_providers.{provider}"
        module = importlib.import_module(module_path)
        ProviderClass = getattr(module, provider_class)
        config_path = Path(config_path)
        auth = ProviderClass(safely_get_settings(config_path=config_path), auth_type="daemon")
        token = auth.get_token()
        assert token is not None, "No token returned from daemon auth"