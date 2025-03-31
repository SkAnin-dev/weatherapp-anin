# Write your tests here. Use only the Django testing framework.

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import City, WeatherReport

class WeatherReportTestCase(TestCase):
    def setUp(self):
        # Creates a test user.
        self.user = User.objects.create_user(username='testuser', password='password')
        # Set up the test client.
        self.client = Client()
        # Creates a sample city.
        self.city = City.objects.create(name="Test City")
        # Creates a sample weather report for the city.
        self.weather_report = WeatherReport.objects.create(
            city=self.city,
            temperature=25.5,
            condition="Clear",
            icon_url="http://example.com/icon.png"
        )

    # Test authentication: Unauthenticated users cannot access city detail view.
    def test_unauthenticated_access(self):
        response = self.client.get(reverse('city-detail', kwargs={'pk': self.city.pk}))
        # Should redirect to login since the view is protected by LoginRequiredMixin.
        self.assertNotEqual(response.status_code, 200)

    # Tests that an authenticated user can access all city views.
    def test_authenticated_city_views(self):
        self.client.login(username='testuser', password='password')
        
        # Test City list view.
        response = self.client.get(reverse('city-list'))
        self.assertEqual(response.status_code, 200)
        
        # Test City detail view.
        response = self.client.get(reverse('city-detail', kwargs={'pk': self.city.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test City create view.
        response = self.client.get(reverse('city-create'))
        self.assertEqual(response.status_code, 200)
        
        # Test City update view.
        response = self.client.get(reverse('city-update', kwargs={'pk': self.city.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test City delete view.
        response = self.client.get(reverse('city-delete', kwargs={'pk': self.city.pk}))
        self.assertEqual(response.status_code, 200)

    # Tests model validation: City uniqueness constraint.
    def test_city_model_unique_constraint(self):
        # Attempting to create a duplicate city should raise an IntegrityError.
        with self.assertRaises(IntegrityError):
            City.objects.create(name="Test City")

    # Tests creation of a WeatherReport and verifies its attributes.
    def test_weather_report_creation(self):
        report = WeatherReport.objects.create(
            city=self.city,
            temperature=18.0,
            condition="Cloudy"
        )
        self.assertEqual(report.city, self.city)
        self.assertEqual(report.temperature, 18.0)
        self.assertEqual(report.condition, "Cloudy")
        self.assertIsNotNone(report.last_updated)

    # Tests API endpoints for cities and weather reports (public access).
    def test_api_endpoints(self):
        # Since API endpoints allow public access (permissions.AllowAny), no login is required.
        response = self.client.get('/api/cities/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/weather-reports/')
        self.assertEqual(response.status_code, 200)

    # Tests view status codes for an authenticated user.
    def test_view_status_codes(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('city-list'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('city-detail', kwargs={'pk': self.city.pk}))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('city-create'))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('city-update', kwargs={'pk': self.city.pk}))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('city-delete', kwargs={'pk': self.city.pk}))
        self.assertEqual(response.status_code, 200)
