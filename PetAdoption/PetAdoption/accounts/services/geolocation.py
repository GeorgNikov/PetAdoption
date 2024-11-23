import requests


def get_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1,
    }
    headers = {
        'User-Agent': 'PetAdoption/1.0 (petadoption.smtp@gmail.com)',  # Replace with your app info
    }
    response = requests.get(url, params=params, headers=headers)
    print(response)
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return float(location['lat']), float(location['lon'])  # Note: 'lat' and 'lon' keys, not 'latitude'/'longitude'
    return None, None
