"""Local JSON-backed user store with PBKDF2 password hashing.

User data is stored outside the source tree by default. Set NLPAPP_DATA_DIR to
choose another writable directory.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import tempfile
from pathlib import Path
from typing import Any

_ITERATIONS = 600_000
_HASH_NAME = "pbkdf2_sha256"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class DatabaseError(RuntimeError):
    """Raised when the local user database cannot be read or written."""


class Database:
    def __init__(self, data_file: str | Path | None = None) -> None:
        if data_file is not None:
            self.data_file = Path(data_file).expanduser()
        else:
            configured_dir = os.environ.get("NLPAPP_DATA_DIR")
            data_dir = (
                Path(configured_dir).expanduser()
                if configured_dir
                else Path.home() / ".nlpapp"
            )
            self.data_file = data_dir / "db.json"

        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_file()

    @staticmethod
    def _normalise_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _hash_password(password: str, salt: bytes | None = None) -> str:
        salt = salt or secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, _ITERATIONS
        )
        return f"{_HASH_NAME}${_ITERATIONS}${salt.hex()}${digest.hex()}"

    @staticmethod
    def _verify_password(password: str, encoded: str) -> bool:
        try:
            algorithm, iterations, salt_hex, digest_hex = encoded.split("$", 3)
            if algorithm != _HASH_NAME:
                return False
            calculated = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
            return hmac.compare_digest(calculated.hex(), digest_hex)
        except (ValueError, TypeError):
            return False

    def _read(self) -> dict[str, Any]:
        if not self.data_file.exists():
            return {"version": 2, "users": {}}
        try:
            with self.data_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise DatabaseError(
                "The user database could not be read. Check its file and permissions."
            ) from exc

        if not isinstance(data, dict):
            raise DatabaseError("The user database has an invalid format.")
        if data.get("version") == 2 and isinstance(data.get("users"), dict):
            return data
        raise DatabaseError("The user database has an unsupported format.")

    def _write(self, data: dict[str, Any]) -> None:
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.data_file.parent,
                delete=False,
            ) as handle:
                temp_name = handle.name
                json.dump(data, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.data_file)
        except OSError as exc:
            if temp_name:
                try:
                    os.unlink(temp_name)
                except OSError:
                    pass
            raise DatabaseError(
                "The user database could not be saved. Check disk space and permissions."
            ) from exc

    def _migrate_legacy_file(self) -> None:
        """Migrate the old source-tree db.json format without losing accounts."""
        legacy_file = Path(__file__).with_name("db.json")
        if self.data_file.exists() or not legacy_file.exists():
            return
        try:
            with legacy_file.open("r", encoding="utf-8") as handle:
                legacy = json.load(handle)
            if not isinstance(legacy, dict):
                raise ValueError("Legacy database must be a JSON object.")

            users = {}
            for email, record in legacy.items():
                if (
                    isinstance(email, str)
                    and isinstance(record, list)
                    and len(record) >= 2
                    and isinstance(record[0], str)
                    and isinstance(record[1], str)
                ):
                    users[self._normalise_email(email)] = {
                        "name": record[0].strip(),
                        "password_hash": self._hash_password(record[1]),
                    }
            self._write({"version": 2, "users": users})
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise DatabaseError(
                "The old user database could not be migrated safely."
            ) from exc

    def add_data(self, name: str, email: str, password: str) -> int:
        name = name.strip()
        email = self._normalise_email(email)
        if not name or not _EMAIL_RE.fullmatch(email) or len(password) < 8:
            raise ValueError(
                "Enter a name, a valid email address, and a password of at least 8 characters."
            )

        data = self._read()
        users = data["users"]
        if email in users:
            return 0

        users[email] = {
            "name": name,
            "password_hash": self._hash_password(password),
        }
        self._write(data)
        return 1

    def search(self, email: str, password: str) -> int:
        email = self._normalise_email(email)
        data = self._read()
        record = data["users"].get(email)
        if not isinstance(record, dict):
            return 0

        encoded = record.get("password_hash")
        if not isinstance(encoded, str):
            return 0
        return int(self._verify_password(password, encoded))
