from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag Objects"""
    class Meta:
        model = Tag
        fields = ('id', 'name',)


class IngredientSerializer(serializers.ModelSerializer):
    """serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name',)


class RecipeSerializer(serializers.ModelSerializer):
    """serializer for recipe objects"""
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'ingredients', 'tags', 'time_in_minutes',
            'price', 'link',
        )


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize Recipe Detail"""
    ingredients = IngredientSerializer(many=True,
                                       read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image to recipe"""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
