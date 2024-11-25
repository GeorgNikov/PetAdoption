import json
import os

from django.conf import settings
from rest_framework.reverse import reverse_lazy


def load_bulgarian_cities():
    # Define the path to the JSON file
    file_path = os.path.join(settings.BASE_DIR, 'staticfiles/json', 'bulgarian_cities.json')

    # Load the JSON data
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract only the city names and format them as choices
    city_choices = [(item["city"], item["city"]) for item in data]
    return city_choices


def redirect_ot_profile(user):
    if hasattr(user, 'adopter'):
        return reverse_lazy('user_profile', kwargs={'pk': user.profile.pk})
    elif hasattr(user, 'shelter'):
        return reverse_lazy('shelter_profile', kwargs={'pk': user.shelter.pk})


