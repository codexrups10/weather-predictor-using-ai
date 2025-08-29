from django.test import TestCase, Client
from django.urls import reverse
import json

class WeatherPredictorTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_index_page(self):
        """Test that the main page loads successfully"""
        response = self.client.get(reverse('weather_predictor:index'))
        self.assertEqual(response.status_code, 200)

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get(reverse('weather_predictor:health_check'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('success', data)

    def test_model_info(self):
        """Test the model info endpoint"""
        response = self.client.get(reverse('weather_predictor:model_info'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('model_info', data)

    def test_predict_weather_valid_input(self):
        """Test weather prediction with valid city name"""
        payload = {'city': 'New York'}
        response = self.client.post(
            reverse('weather_predictor:predict_weather'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('success', data)

    def test_predict_weather_empty_city(self):
        """Test weather prediction with empty city name"""
        payload = {'city': ''}
        response = self.client.post(
            reverse('weather_predictor:predict_weather'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
