"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params: dict):
    """Create and return new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self) -> None:
        """Set up variables."""
        self.client = APIClient()

        self.payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }

        self.user_model = get_user_model()

    def test_create_user_success(self):
        """Test creating a user is successful."""

        res = self.client.post(CREATE_USER_URL, self.payload)

        if res.status_code != status.HTTP_201_CREATED:
            print(f"Response content: {res.content}")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = self.user_model.objects.get(email=self.payload["email"])
        self.assertTrue(user.check_password(self.payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""

        create_user(**self.payload)

        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error returned if password less than 5 characters"""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test Name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = self.user_model.objects.filter(email=payload["email"]).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "testpassword123",
        }
        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test return error if credentials invalid."""

        create_user(email="test@example.com", password="goodpass")

        payload = {
            "email": "test@example.com",
            "password": "badpass",
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password return an error."""
        payload = {
            "email": "test@example.com",
            "password": "",
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""

        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test API requests that require authentication."""

    def setUp(self) -> None:
        self.user = create_user(
            email="test@example.com",
            password="password123",
            name="Test User",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "name": self.user.name,
                "email": self.user.email,
            },
        )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {
            "name": "Update Name",
            "password": "updatepassword",
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
