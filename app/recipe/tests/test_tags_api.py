from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required is for listing tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code,
                         status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test the private available tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test@pass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_tags(self):
        """Test  retreiving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limted_to_user(self):
        """Test that tags are returned for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )

        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user,
                                 name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tags_successfull(self):
        """Test that tags can be created"""
        payload = {'name': 'breakfast'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=self.user,
                                    name=payload['name']
                                    ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='BreakFast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')

        recipe = Recipe.objects.create(
            title='Aloo Parantha',
            time_in_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique tags"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')

        recipe1 = Recipe.objects.create(
            title='Pancackes',
            time_in_minutes=10,
            price=10,
            user=self.user
        )
        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
            title='Gobi Paranthe',
            time_in_minutes=15,
            price=12,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
