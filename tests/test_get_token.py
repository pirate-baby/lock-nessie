from pytest import mark as m
import re
import importlib
import sys
import time
import signal
import multiprocessing
import io
import subprocess
import textwrap
import os

login_url_regex = {
    "microsoft": r"https://login.microsoftonline.com/common/oauth2\S+",
}

@m.describe("When getting a token")
class TestProviders:

    @m.parametrize(
        "patched_settings",
        [("microsoft", "user")],
        indirect=True
    )
    @m.context("and the user flow is selected")
    @m.context("and no cache exists")
    @m.it("tests that the login URL is printed to stdout")
    def test_get_token_user_no_cache(self, patched_settings):
        provider, user_type, config_dir = patched_settings
        provider_class = f"{provider.capitalize()}Auth"

        # Script to run in subprocess
        script = textwrap.dedent(f'''
            import importlib
            from locknessie.auth_providers.{provider} import {provider_class}
            auth = {provider_class}(auth_type="{user_type}")
            auth.get_token()
        ''')

        env = os.environ.copy()
        env["LOCKNESSIE_CONFIG_PATH"] = config_dir

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
