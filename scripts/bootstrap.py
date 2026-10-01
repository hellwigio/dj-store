"""Create local secrets without overwriting an existing environment."""

import os
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / ".env"
try:
    with open(target, "x", opener=lambda path, flags: os.open(path, flags, 0o600)) as f:
        f.write(
            (root / ".env.example")
            .read_text()
            .replace("replace-with-generated-secret", secrets.token_urlsafe(64))
        )
except FileExistsError:
    print(".env already exists; unchanged")
else:
    print("Created .env with a unique secret (permissions 0600)")
