"""
    Test for the tags APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from recipe.serializers import TagSerializer
from core.models import Tag, Recipe

from rest_framework.test import APIClient
from rest_framework import status


TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(**params):
    """Create and return a new user."""
    default = {
        "email": "user@example.com",
        "password": "testpassword",
        "name": "Test User",
    }
    default.update(params)

    return get_user_model().objects.create_user(**default)


class PublicTagsAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrive_tags(self):
        """Test retriving a list of tags."""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email="usertest@gmail.com")
        Tag.objects.create(user=user2, name="Vegan")
        tag = Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name="Befor")

        payload = {"name": "After"}

        url = detail_url(tag.id)

        res = self.client.patch(url, payload)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload.get("name"))

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name="My Tag")

        url = detail_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())
