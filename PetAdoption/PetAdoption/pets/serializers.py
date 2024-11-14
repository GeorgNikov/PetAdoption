from rest_framework import serializers
from .models import Pet

class PetSerializer(serializers.ModelSerializer):
    # total_likes = serializers.ReadOnlyField()

    class Meta:
        model = Pet
        fields = ['id', 'name', 'breed', 'age', 'type', 'image']
