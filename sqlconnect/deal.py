from geopy.geocoders import Nominatim
geolocator = Nominatim()
location = geolocator.reverse("28.5097, 119.534")
print(location.raw['address'])