from django.test import TestCase
from .models import Restaurant

# Create your tests here.


class RestaurantTests(TestCase):
    def test_restaurant_property_name(self):
        restaurant = Restaurant(name="test")

        self.assertEqual(restaurant.restaurant_name, 'test')

        restaurant.nickname = "westlyFoods"

        self.assertEqual(restaurant.restaurant_name, "westlyFoods")
