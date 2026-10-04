import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from src import teacher_auth
from src.app import app, activities


class AdminModeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.teachers_file = Path(self.temp_directory.name) / "teachers.json"
        self.teachers_file.write_text('{"teachers": {}}', encoding="utf-8")
        patcher = patch.object(teacher_auth, "TEACHERS_FILE", self.teachers_file)
        patcher.start()
        self.addCleanup(patcher.stop)

        teachers = teacher_auth.load_teachers()
        teachers["coach"] = teacher_auth.hash_password("correct-horse-battery")
        self.teachers_file.write_text(
            json.dumps({"teachers": teachers}), encoding="utf-8"
        )

        self.activity_name = "Admin Mode Test Activity"
        activity_patcher = patch.dict(
            activities,
            {
                self.activity_name: {
                    "description": "Test activity",
                    "schedule": "Fridays",
                    "max_participants": 10,
                    "participants": [],
                }
            },
        )
        activity_patcher.start()
        self.addCleanup(activity_patcher.stop)
        transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=transport, base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_missing_teacher_file_allows_public_read_only_mode(self):
        missing_file = Path(self.temp_directory.name) / "missing-teachers.json"
        with patch.object(teacher_auth, "TEACHERS_FILE", missing_file):
            self.assertEqual(teacher_auth.load_teachers(), {})
            self.assertEqual((await self.client.get("/activities")).status_code, 200)
            response = await self.client.post(
                f"/activities/{self.activity_name}/signup",
                params={"email": "student@example.edu"},
            )
            self.assertEqual(response.status_code, 401)

    async def test_activities_remain_public_but_writes_require_teacher(self):
        self.assertEqual((await self.client.get("/activities")).status_code, 200)
        signup = await self.client.post(
            f"/activities/{self.activity_name}/signup",
            params={"email": "student@example.edu"},
        )
        unregister = await self.client.delete(
            f"/activities/{self.activity_name}/unregister",
            params={"email": "student@example.edu"},
        )
        self.assertEqual(signup.status_code, 401)
        self.assertEqual(unregister.status_code, 401)

    async def test_invalid_credentials_are_rejected(self):
        response = await self.client.post(
            "/auth/login", json={"username": "coach", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 401)

    async def test_teacher_can_sign_up_and_unregister_students(self):
        login = await self.client.post(
            "/auth/login",
            json={"username": "coach", "password": "correct-horse-battery"},
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn("httponly", login.headers["set-cookie"].lower())

        signup = await self.client.post(
            f"/activities/{self.activity_name}/signup",
            params={"email": "student@example.edu"},
        )
        self.assertEqual(signup.status_code, 200)

        unregister = await self.client.delete(
            f"/activities/{self.activity_name}/unregister",
            params={"email": "student@example.edu"},
        )
        self.assertEqual(unregister.status_code, 200)

        await self.client.post("/auth/logout")
        self.assertEqual(
            (await self.client.post(
                f"/activities/{self.activity_name}/signup",
                params={"email": "student@example.edu"},
            )).status_code,
            401,
        )


if __name__ == "__main__":
    unittest.main()
