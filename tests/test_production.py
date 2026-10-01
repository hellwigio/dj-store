import os
import subprocess
import sys

import pytest


def run_production(**overrides):
    env = {
        k: v for k, v in os.environ.items() if not k.startswith("DJANGO_") and k != "DATABASE_URL"
    }
    env.update(
        {
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
            "DJANGO_SECRET_KEY": "test-only-abcdefghijklmnopqrstuvwxyz0123456789-ABCDEFGHIJK",
            "DJANGO_ALLOWED_HOSTS": "example.com",
            "DATABASE_URL": "postgresql://app:unused@localhost/app",
            **overrides,
        }
    )
    return subprocess.run(
        [sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"],
        env=env,
        capture_output=True,
        text=True,
    )


def test_production_deploy_checks():
    result = run_production(DJANGO_HSTS_INCLUDE_SUBDOMAINS="true", DJANGO_HSTS_PRELOAD="true")
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "overrides",
    [
        {"DJANGO_SECRET_KEY": "short"},
        {"DJANGO_ALLOWED_HOSTS": "*"},
        {"DJANGO_ALLOWED_HOSTS": ""},
        {"DATABASE_URL": "sqlite:///db.sqlite3"},
    ],
)
def test_production_rejects_unsafe_config(overrides):
    assert run_production(**overrides).returncode != 0


def test_default_hsts_requires_domain_review():
    result = run_production()
    assert "security.W005" in result.stderr
    assert "security.W021" in result.stderr
    assert "2 issues" in result.stderr
