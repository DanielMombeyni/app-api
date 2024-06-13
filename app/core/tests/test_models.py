from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_user(email="test@example.com", password="testpassword"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def test_create_user_with_email_successfully(self):
        email = "test@gmail.com"
        password = "testpassword"
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test@GMAIL.com", "test@gmail.com"],
            ["Test1@Gmail.com", "Test1@gmail.com"],
            ["TEST2@GMAIL.COM", "TEST2@gmail.com"],
            ["test3@gmail.COM", "test3@gmail.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            "test@gmail.com",
            "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test123",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="recipe title",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description",
        )

        self.assertTrue(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="tage1")

        self.assertEqual(str(tag), tag.name)
