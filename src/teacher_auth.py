import hashlib
import json
import secrets
from pathlib import Path


TEACHERS_FILE = Path(__file__).with_name("teachers.json")
PASSWORD_ITERATIONS = 600_000


def load_teachers() -> dict[str, dict[str, str]]:
    if not TEACHERS_FILE.exists():
        return {}

    data = json.loads(TEACHERS_FILE.read_text(encoding="utf-8"))
    teachers = data.get("teachers")
    if not isinstance(teachers, dict):
        raise ValueError("teachers.json must contain a 'teachers' object")
    return teachers


def hash_password(password: str) -> dict[str, str]:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return {"salt": salt.hex(), "password_hash": password_hash.hex()}


def verify_password(password: str, credentials: dict[str, str]) -> bool:
    try:
        salt = bytes.fromhex(credentials["salt"])
        expected_hash = bytes.fromhex(credentials["password_hash"])
    except (KeyError, ValueError):
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return secrets.compare_digest(actual_hash, expected_hash)
