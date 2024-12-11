import json
import os

from django.conf import settings
from rest_framework.reverse import reverse_lazy

from PetAdoption.accounts.choices import BulgarianProvinces


def load_bulgarian_cities():
    # Define the path to the JSON file
    file_path = os.path.join(settings.BASE_DIR, 'staticfiles/json', 'bulgarian_cities.json')

    # Load the JSON data
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract only the city names and format them as choices
    city_choices = [(item["city"], item["city"]) for item in data]
    return city_choices


# def redirect_to_profile(user):
#     if hasattr(user, 'adopter'):
#         return reverse_lazy('user_profile', kwargs={'pk': user.profile.pk})
#     elif hasattr(user, 'shelter'):
#         return reverse_lazy('shelter_profile', kwargs={'pk': user.shelter.pk})
#     else:
#         return reverse_lazy('index')


def load_cities_and_provinces():
    cities = load_bulgarian_cities()
    city_names = [city[1] for city in cities]

    provinces = [province[1] for province in BulgarianProvinces.choices]

    return city_names, provinces
