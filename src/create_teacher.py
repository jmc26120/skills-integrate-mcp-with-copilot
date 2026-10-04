import argparse
import getpass
import json

from src.teacher_auth import TEACHERS_FILE, hash_password, load_teachers


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a teacher login for Mergington")
    parser.add_argument("username", help="Teacher username")
    username = parser.parse_args().username

    password = getpass.getpass("Password (at least 12 characters): ")
    if len(password) < 12:
        parser.error("Password must be at least 12 characters")
    if password != getpass.getpass("Confirm password: "):
        parser.error("Passwords do not match")

    teachers = load_teachers()
    if username in teachers:
        parser.error(f"Teacher '{username}' already exists")

    teachers[username] = hash_password(password)
    TEACHERS_FILE.write_text(
        json.dumps({"teachers": teachers}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created teacher account '{username}'.")


if __name__ == "__main__":
    main()
