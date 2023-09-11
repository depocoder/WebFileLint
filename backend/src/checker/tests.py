import os

from django.contrib.auth.models import User
from django.test import Client
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import File, LintFile


class FileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

    def test_create_file(self):
        url = reverse("file-list")
        file_path = os.path.join(settings.BASE_DIR, 'checker', 'tests.py')
        with open(file_path, "rb") as file:
            data = {
                "file_name": "tests.py",
                "raw_file": file,
                "user": reverse("user-detail", args=[self.user.id]),
            }
            response = self.client.post(url, data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            file = File.objects.get(id=response.data["id"])
            self.assertEqual(file.file_name, "tests.py")

    def test_retrieve_file(self):
        file = File.objects.create(file_name="test.py", user=self.user)
        url = reverse("file-detail", args=[file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["file_name"], "test.py")

    def test_list_files(self):
        File.objects.create(file_name="test1.py", user=self.user)
        File.objects.create(file_name="test2.py", user=self.user)
        url = reverse("file-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["file_name"], "test1.py")
        self.assertEqual(response.data[1]["file_name"], "test2.py")

    def test_update_file(self):
        file = File.objects.create(file_name="test.py", user=self.user)
        url = reverse("file-detail", args=[file.id])
        data = {"file_name": "updated.py"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        file.refresh_from_db()
        self.assertEqual(file.file_name, "updated.py")

    def test_delete_file(self):
        file = File.objects.create(file_name="test.py", user=self.user)
        url = reverse("file-detail", args=[file.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        file.refresh_from_db()
        self.assertTrue(file.is_deleted)


class LintFileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

    def test_retrieve_lint_file(self):
        file = File.objects.create(file_name="test.py", user=self.user)
        lint_file = LintFile.objects.create(raw_file=file, linter="flake8")
        url = reverse("lintfile-detail", args=[lint_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["linter"], "flake8")

    def test_list_lint_files(self):
        file = File.objects.create(file_name="test.py", user=self.user)
        LintFile.objects.create(raw_file=file, linter="flake8")
        LintFile.objects.create(raw_file=file, linter="mypy")
        url = reverse("lintfile-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["linter"], "flake8")
        self.assertEqual(response.data[1]["linter"], "mypy")


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_users(self):
        user1 = User.objects.create(username="user1", email="user1@example.com")
        user2 = User.objects.create(username="user2", email="user2@example.com")
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Including the authenticated user
        usernames = [data["username"] for data in response.data]
        self.assertIn("testuser", usernames)
        self.assertIn("user1", usernames)
        self.assertIn("user2", usernames)

    def test_retrieve_user(self):
        url = reverse("user-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")


class FileDetailTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.file = File.objects.create(file_name="test.py", user=self.user)

    def test_file_detail(self):
        url = reverse("file-detail", args=[self.file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["file_name"], "test.py")

    def test_file_detail_unauthorized(self):
        self.client.logout()
        url = reverse("file-detail", args=[self.file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_file_detail_other_user(self):
        other_user = User.objects.create_user(username="otheruser", password="testpassword")
        self.client.force_authenticate(user=other_user)
        url = reverse("file-detail", args=[self.file.id])
        response = self.client.get(url)
        self.assertNotEquals(response.status_code, status.HTTP_200_OK)


class HomePageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user=self.user)

    def test_home_page(self):
        url = reverse("home_page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert the content of the response, if applicable


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_view(self):
        url = reverse("register_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert the content of the response, if applicable


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_view(self):
        url = reverse("login_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert the content of the response, if applicable
