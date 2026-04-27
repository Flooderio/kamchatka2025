import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from ecoapp.bot.handlers import save_and_render_result, start_handler
from ecoapp.models import CalculationResult, Route, SurveyLocal, SurveyTourist
from ecoapp.services.calculation import calculate_survey


class BaseSeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_reference_data")


class CalculationServiceTests(BaseSeededTestCase):
    def test_tourist_calculation_returns_positive_total(self):
        route = Route.objects.get(code="avacha")
        from ecoapp.models import City, TransportType

        answers = {
            "age": 30,
            "route": route,
            "departure_city": City.objects.get(name="Москва"),
            "is_transfer_in_moscow": True,
            "flight_class": "economy",
            "days_in_location": 5,
            "accommodation_type": "hotel",
            "people_in_room": 2,
            "meal_type": "standard",
            "meals_per_day": 3,
            "waste_management": "sort",
            "local_transport_choices": [TransportType.objects.get(code="jeep")],
            "tours": [],
            "boat_trip_duration": "none",
            "helicopter_ride_duration": None,
            "helicopter_ride_passengers": None,
        }
        outcome = calculate_survey("tourist", answers)
        self.assertGreater(outcome.total_emission, 0)
        self.assertIn("flight", outcome.breakdown)

    def test_local_calculation_returns_positive_total(self):
        outcome = calculate_survey(
            "local",
            {
                "age": 40,
                "housing_type": "apartment",
                "housing_area": 70,
                "people_in_home": 3,
                "heating_source": "central",
                "personal_transport": "car",
                "fuel_type": "gasoline",
                "average_mileage_per_month": 800,
                "public_transport_usage": "1_3_per_week",
                "flights_in_last_year": "domestic",
                "flights_per_year": 2,
                "flight_type": "economy",
                "waste_management": "separate_collection",
            },
        )
        self.assertGreater(outcome.total_emission, 0)
        self.assertIn("housing", outcome.breakdown)


class WebFlowTests(BaseSeededTestCase):
    def setUp(self):
        self.client = Client()

    def test_tourist_form_creates_result(self):
        from ecoapp.models import City, TransportType

        route = Route.objects.get(code="avacha")
        city = City.objects.get(name="Москва")
        jeep = TransportType.objects.get(code="jeep")
        response = self.client.post(
            reverse("tourist_survey"),
            data={
                "age": 29,
                "route": route.pk,
                "departure_city": city.pk,
                "is_transfer_in_moscow": "True",
                "flight_class": "economy",
                "days_in_location": 4,
                "accommodation_type": "hotel",
                "people_in_room": 2,
                "meal_type": "standard",
                "meals_per_day": 3,
                "waste_management": "sort",
                "local_transport_choices": [jeep.pk],
                "boat_trip_duration": "none",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Итоговый углеродный след")
        self.assertEqual(CalculationResult.objects.count(), 1)
        self.assertEqual(SurveyTourist.objects.count(), 1)

    def test_local_api_creates_result(self):
        response = self.client.post(
            reverse("api_calculate_local"),
            data=json.dumps(
                {
                    "age": 37,
                    "housing_type": "apartment",
                    "housing_area": 50,
                    "people_in_home": 2,
                    "heating_source": "central",
                    "personal_transport": "none",
                    "fuel_type": "none",
                    "average_mileage_per_month": 0,
                    "public_transport_usage": "daily",
                    "flights_in_last_year": "none",
                    "flights_per_year": 0,
                    "flight_type": "economy",
                    "waste_management": "separate_collection",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CalculationResult.objects.count(), 1)
        self.assertEqual(SurveyLocal.objects.count(), 1)


class BotHandlerTests(BaseSeededTestCase):
    def test_save_and_render_result(self):
        from ecoapp.models import City, TransportType

        message = SimpleNamespace(from_user=SimpleNamespace(id=12345))
        text = save_and_render_result(
            message,
            "tourist",
            {
                "age": 0,
                "route": Route.objects.get(code="avacha"),
                "departure_city": City.objects.get(name="Москва"),
                "is_transfer_in_moscow": False,
                "flight_class": "economy",
                "days_in_location": 3,
                "accommodation_type": "tent",
                "people_in_room": 2,
                "meal_type": "local",
                "meals_per_day": 2,
                "waste_management": "minimize",
                "local_transport_choices": [TransportType.objects.get(code="jeep")],
                "tours": [],
                "boat_trip_duration": "none",
                "helicopter_ride_duration": None,
                "helicopter_ride_passengers": None,
            },
        )
        self.assertIn("Расчет завершен", text)
        self.assertEqual(CalculationResult.objects.count(), 1)

    def test_start_handler_sends_welcome_message(self):
        message = SimpleNamespace(answer=AsyncMock())
        state = SimpleNamespace(clear=AsyncMock())
        asyncio.run(start_handler(message, state))
        self.assertTrue(message.answer.await_count >= 1)
from django.test import TestCase

# Create your tests here.
