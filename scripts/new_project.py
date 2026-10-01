"""Usage: python scripts/new_project.py ../my-project"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description="Create a fresh project from this template")
parser.add_argument("destination", type=Path)
args = parser.parse_args()
source = Path(__file__).resolve().parents[1]
destination = args.destination.resolve()
if destination.exists() or destination.is_relative_to(source):
    parser.error("Destination must not exist and must be outside the template directory")
name = destination.name
if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
    parser.error("Project directory name must match [a-z][a-z0-9-]*")
shutil.copytree(
    source,
    destination,
    ignore=shutil.ignore_patterns(
        ".git",
        ".agents",
        ".codex",
        ".venv",
        ".env",
        ".env.production",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "*.sqlite3*",
        "*.pyc",
        "staticfiles",
        "media",
        ".coverage",
        "htmlcov",
    ),
)
# Exclude all private environment variants, while keeping documented examples.
for path in destination.glob(".env.*"):
    if path.name not in {".env.example", ".env.production.example"}:
        path.unlink()
project = destination / "pyproject.toml"
project.write_text(project.read_text().replace('name = "django-starter"', f'name = "{name}"', 1))
# A virtual root package is recorded in uv.lock as well; retain dependency versions.
lock = destination / "uv.lock"
if lock.exists():
    lock.write_text(lock.read_text().replace('name = "django-starter"', f'name = "{name}"'))
subprocess.run([sys.executable, str(destination / "scripts/bootstrap.py")], check=True)
print(f"Created {destination}\nNext: cd {destination} && uv sync --locked")
