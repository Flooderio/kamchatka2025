from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

from ecoapp.models import City, EmissionFactor, FactorSet, Route, TransportType


KAMCHATKA_CITY_NAME = "Петропавловск-Камчатский"


@dataclass
class CalculationOutcome:
    user_type: str
    route: Route | None
    factor_set: FactorSet | None
    answers: dict
    breakdown: dict[str, float]
    total_emission: float


class FactorResolver:
    def __init__(self, factor_set: FactorSet | None = None):
        self.factor_set = factor_set or FactorSet.objects.filter(is_active=True).order_by("-created_at").first()
        self._cache: dict[tuple[str, str], float] = {}

    def get(self, category: str, subtype: str, default: float = 0.0) -> float:
        key = (category, subtype)
        if key in self._cache:
            return self._cache[key]
        if not self.factor_set:
            self._cache[key] = default
            return default
        factor = EmissionFactor.objects.filter(
            factor_set=self.factor_set,
            category=category,
            subtype=subtype,
        ).first()
        value = factor.value if factor else default
        self._cache[key] = value
        return value


def calculate_survey(user_type: str, answers: dict, factor_set: FactorSet | None = None) -> CalculationOutcome:
    resolver = FactorResolver(factor_set=factor_set)
    if user_type == "tourist":
        return calculate_tourist_footprint(answers, resolver)
    if user_type == "local":
        return calculate_local_footprint(answers, resolver)
    raise ValueError(f"Unsupported user_type: {user_type}")


def calculate_tourist_footprint(answers: dict, resolver: FactorResolver) -> CalculationOutcome:
    departure_city = answers["departure_city"]
    route = answers.get("route")
    transport_types = list(answers.get("local_transport_choices", []))
    days = int(answers["days_in_location"])
    room_size = max(int(answers["people_in_room"]), 1)
    meals_per_day = int(answers["meals_per_day"])
    helicopter_minutes = int(answers.get("helicopter_ride_duration") or 0)
    helicopter_passengers = max(int(answers.get("helicopter_ride_passengers") or 1), 1)

    flight_factor = resolver.get("flight", answers["flight_class"], default=0.133)
    flight_distance = get_round_trip_distance_km(departure_city)
    if answers.get("is_transfer_in_moscow"):
        flight_distance *= resolver.get("flight_modifier", "transfer_moscow", default=1.15)
    flight_total = flight_distance * flight_factor

    accommodation_factor = resolver.get(
        "accommodation",
        answers["accommodation_type"],
        default=20.0,
    )
    accommodation_total = days * accommodation_factor / room_size

    meal_factor = resolver.get("meal", answers["meal_type"], default=2.0)
    meals_total = days * meals_per_day * meal_factor

    waste_factor = resolver.get("tourist_waste", answers["waste_management"], default=0.5)
    waste_total = days * waste_factor

    local_transport_total = calculate_route_transport_total(
        resolver=resolver,
        transport_types=transport_types,
        days=days,
        boat_duration=answers.get("boat_trip_duration") or "none",
        helicopter_minutes=helicopter_minutes,
        helicopter_passengers=helicopter_passengers,
    )

    breakdown = {
        "flight": round(flight_total, 2),
        "accommodation": round(accommodation_total, 2),
        "meals": round(meals_total, 2),
        "waste": round(waste_total, 2),
        "local_transport": round(local_transport_total, 2),
    }
    total = round(sum(breakdown.values()), 2)
    return CalculationOutcome(
        user_type="tourist",
        route=route,
        factor_set=resolver.factor_set,
        answers=serialize_answers(answers),
        breakdown=breakdown,
        total_emission=total,
    )


def calculate_local_footprint(answers: dict, resolver: FactorResolver) -> CalculationOutcome:
    area = int(answers["housing_area"])
    residents = max(int(answers["people_in_home"]), 1)
    annual_mileage = int(answers["average_mileage_per_month"]) * 12
    flights_per_year = int(answers.get("flights_per_year") or 0)

    housing_base = resolver.get("housing_base", answers["housing_type"], default=0.8)
    heating_factor = resolver.get("heating", answers["heating_source"], default=0.4)
    housing_total = (area * (housing_base + heating_factor) * 12) / residents

    personal_transport_total = 0.0
    if answers["personal_transport"] != "none":
        fuel_factor = resolver.get("fuel", answers["fuel_type"], default=0.192)
        vehicle_multiplier = resolver.get(
            "vehicle_multiplier",
            answers["personal_transport"],
            default=1.0,
        )
        personal_transport_total = annual_mileage * fuel_factor * vehicle_multiplier

    public_transport_total = resolver.get(
        "public_transport",
        answers["public_transport_usage"],
        default=120.0,
    )
    waste_total = resolver.get("local_waste", answers["waste_management"], default=48.0)

    flight_total = 0.0
    if answers["flights_in_last_year"] != "none" and flights_per_year:
        flight_subtype = f'{answers["flights_in_last_year"]}_{answers["flight_type"]}'
        flight_total = flights_per_year * resolver.get(
            "annual_flight",
            flight_subtype,
            default=290.0,
        )

    breakdown = {
        "housing": round(housing_total, 2),
        "personal_transport": round(personal_transport_total, 2),
        "public_transport": round(public_transport_total, 2),
        "flights": round(flight_total, 2),
        "waste": round(waste_total, 2),
    }
    total = round(sum(breakdown.values()), 2)
    return CalculationOutcome(
        user_type="local",
        route=None,
        factor_set=resolver.factor_set,
        answers=serialize_answers(answers),
        breakdown=breakdown,
        total_emission=total,
    )


def calculate_route_transport_total(
    resolver: FactorResolver,
    transport_types: Iterable[TransportType],
    days: int,
    boat_duration: str,
    helicopter_minutes: int,
    helicopter_passengers: int,
) -> float:
    total = 0.0
    codes = {transport.code for transport in transport_types if transport.code}
    for code in codes:
        if code == "boat":
            if boat_duration and boat_duration != "none":
                total += resolver.get("boat", boat_duration, default=45.0)
            continue
        if code == "helicopter":
            hours = helicopter_minutes / 60 if helicopter_minutes else 0
            total += hours * resolver.get("local_transport", "helicopter", default=150.0) / helicopter_passengers
            continue
        total += days * resolver.get("local_transport", code, default=12.0)
    return total


def get_round_trip_distance_km(departure_city: City) -> float:
    destination = City.objects.filter(name=KAMCHATKA_CITY_NAME).first()
    if not destination:
        return 6800.0
    one_way = haversine_km(departure_city.lat, departure_city.lon, destination.lat, destination.lon)
    return round(one_way * 2, 2)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    origin_lat = radians(lat1)
    destination_lat = radians(lat2)
    distance = (
        sin(d_lat / 2) ** 2
        + cos(origin_lat) * cos(destination_lat) * sin(d_lon / 2) ** 2
    )
    return 2 * radius * asin(sqrt(distance))


def serialize_answers(answers: dict) -> dict:
    serialized = {}
    for key, value in answers.items():
        if hasattr(value, "pk"):
            serialized[key] = value.pk
        elif isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
            serialized[key] = [item.pk if hasattr(item, "pk") else item for item in value]
        else:
            serialized[key] = value
    return serialized
