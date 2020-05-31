from rest_framework import serializers

from core.models import Tag, Ingredient


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
