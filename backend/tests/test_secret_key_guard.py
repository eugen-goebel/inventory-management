"""Tests for the JWT secret key guard.

The development default is a string in a public repository, so any token
signed with it can be forged. APP_ENV=production makes the service refuse to
start rather than serve on that key.

These run in a subprocess: the key is read at import time, and reimporting a
module with a different environment is not something os.environ can undo
between test cases.
"""

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

PROBE = "import agents.auth_service as a; print('SECRET=' + a.SECRET_KEY)"

DEV_SECRET = "dev-secret-change-in-production"


def _run(env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Import auth_service in a clean environment and report what happened."""
    full_env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR)}
    for var in ("JWT_SECRET_KEY", "APP_ENV"):
        full_env.pop(var, None)
    if env:
        full_env.update(env)

    return subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=BACKEND_DIR,
        env=full_env,
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestSecretKeyGuard:
    def test_development_falls_back_to_the_default(self):
        """Without APP_ENV the default applies, so a checkout runs with no setup."""
        result = _run()
        assert result.returncode == 0, result.stderr
        assert f"SECRET={DEV_SECRET}" in result.stdout

    def test_development_warns_about_the_default(self):
        """The fallback is logged, otherwise it is invisible."""
        result = _run()
        assert "JWT_SECRET_KEY is not set" in result.stderr

    def test_production_without_a_key_refuses_to_start(self):
        """APP_ENV=production and no key is a startup error, not a silent default."""
        result = _run({"APP_ENV": "production"})
        assert result.returncode != 0
        assert "JWT_SECRET_KEY must be set" in result.stderr

    def test_production_rejects_the_development_default(self):
        """Copying the default out of the repo into the environment is caught."""
        result = _run({"APP_ENV": "production", "JWT_SECRET_KEY": DEV_SECRET})
        assert result.returncode != 0
        assert "development default" in result.stderr

    def test_production_with_a_real_key_starts(self):
        """A proper key in production is accepted."""
        result = _run({"APP_ENV": "production", "JWT_SECRET_KEY": "a-real-key"})
        assert result.returncode == 0, result.stderr
        assert "SECRET=a-real-key" in result.stdout

    def test_app_env_is_case_insensitive(self):
        """APP_ENV=Production behaves like production, a plausible typo."""
        result = _run({"APP_ENV": "Production"})
        assert result.returncode != 0
        assert "JWT_SECRET_KEY must be set" in result.stderr

    def test_a_key_without_app_env_is_still_used(self):
        """Setting only the key works, which is what most deployments do."""
        result = _run({"JWT_SECRET_KEY": "a-real-key"})
        assert result.returncode == 0, result.stderr
        assert "SECRET=a-real-key" in result.stdout
