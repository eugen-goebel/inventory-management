"""Tests that a .env file is actually loaded.

CONTRIBUTING tells contributors to copy .env.example to .env and fill in
values. Before this, nothing called load_dotenv, so the file was read by
no one: a contributor could set JWT_SECRET_KEY there, see the app start,
and still be signing tokens with the built-in development default.

These tests run main.py in a subprocess with a temporary working directory,
because load_dotenv reads the file at import time and os.environ cannot be
un-imported between test cases.
"""

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Import main so the .env is loaded, then report what auth_service ended up
# using. Printed as a single line so the test can assert on it.
PROBE = (
    "import main; "
    "import agents.auth_service as a; "
    "print('SECRET=' + a.SECRET_KEY); "
    "print('EXPIRE=' + str(a.ACCESS_TOKEN_EXPIRE_MINUTES))"
)


def _run_probe(cwd: Path, env: dict[str, str] | None = None) -> dict[str, str]:
    """Run the probe in a subprocess and parse the values it reports."""
    full_env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR)}
    # Drop anything inherited from the developer's shell so the test is
    # not influenced by a JWT_SECRET_KEY that happens to be exported.
    full_env.pop("JWT_SECRET_KEY", None)
    full_env.pop("JWT_EXPIRE_MINUTES", None)
    if env:
        full_env.update(env)

    result = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=cwd,
        env=full_env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    values = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            values[key] = value
    return values


class TestDotenvLoading:
    def test_env_file_is_read(self, tmp_path):
        """A .env in the working directory sets the JWT secret."""
        (tmp_path / ".env").write_text(
            "JWT_SECRET_KEY=secret-from-the-env-file\nJWT_EXPIRE_MINUTES=15\n"
        )
        values = _run_probe(tmp_path)
        assert values["SECRET"] == "secret-from-the-env-file"
        assert values["EXPIRE"] == "15"

    def test_default_applies_without_env_file(self, tmp_path):
        """Without a .env the built-in development default is used."""
        values = _run_probe(tmp_path)
        assert values["SECRET"] == "dev-secret-change-in-production"
        assert values["EXPIRE"] == "60"

    def test_real_environment_wins_over_env_file(self, tmp_path):
        """An exported variable takes precedence, which is what Docker relies on."""
        (tmp_path / ".env").write_text("JWT_SECRET_KEY=secret-from-the-env-file\n")
        values = _run_probe(tmp_path, {"JWT_SECRET_KEY": "secret-from-the-environment"})
        assert values["SECRET"] == "secret-from-the-environment"
