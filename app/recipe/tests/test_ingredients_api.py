from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code,
                         status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test the private available ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test@pass'
        )

        self.client.force_authenticate(self.user)

    def test_retreive_ingredient_list(self):
        """Tests retreiving a list of Ingredients"""

        Ingredient.objects.create(user=self.user, name='Potato')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients,
                                          many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Tests that only ingredients for
            the authenticated user are returned"""

        user2 = get_user_model().objects.create_user(
            'test2@gmail.com',
            'pass@2'
        )

        Ingredient.objects.create(user=user2,
                                  name='Black Pepper')
        ingredient = Ingredient.objects.create(user=self.user,
                                               name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code,
                         status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'],
                         ingredient.name)
        self.assertEqual(self.user, ingredient.user)

    def test_create_ingredient_successfull(self):
        """Test that ingredient can be created successfully"""

        payload = {'name': 'Potato'}

        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_invalid_ingredient(self):
        """Test creating invalid ingredient fails"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user,
                                                name='Turkey')
        ingredient2 = Ingredient.objects.create(user=self.user,
                                                name='Apples')

        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_in_minutes=5,
            price=10,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user,
                                               name='Potato')
        Ingredient.objects.create(user=self.user,
                                  name='Carrot')

        recipe1 = Recipe.objects.create(
            title='Aloo Pranthe',
            time_in_minutes=10,
            price=20,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Aloo Bread',
            time_in_minutes=15,
            price=5,
            user=self.user
        )

        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
