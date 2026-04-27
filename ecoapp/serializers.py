from rest_framework import serializers

from .models import (
    BOAT_DURATION_CHOICES,
    ACCOMMODATION_TYPE_CHOICES,
    FLIGHT_CLASS_CHOICES,
    FLIGHT_SCOPE_CHOICES,
    FUEL_TYPE_CHOICES,
    HEATING_SOURCE_CHOICES,
    HOUSING_TYPE_CHOICES,
    LOCAL_WASTE_CHOICES,
    MEAL_TYPE_CHOICES,
    PERSONAL_TRANSPORT_CHOICES,
    PUBLIC_TRANSPORT_USAGE_CHOICES,
    TOURIST_WASTE_CHOICES,
    CalculationResult,
    City,
    Route,
    TransportType,
)


class RouteSerializer(serializers.ModelSerializer):
    transport_modes = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = ("id", "code", "name", "description", "default_duration_days", "transport_modes")

    def get_transport_modes(self, obj):
        return [
            {"id": transport.pk, "code": transport.code, "name": transport.type_name}
            for transport in obj.transport_modes.filter(is_active=True)
        ]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "region_name")


class TransportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportType
        fields = ("id", "code", "type_name", "description")


class TouristSurveySerializer(serializers.Serializer):
    age = serializers.IntegerField(min_value=0, max_value=120)
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.filter(is_active=True))
    departure_city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    is_transfer_in_moscow = serializers.BooleanField()
    flight_class = serializers.ChoiceField(choices=[choice[0] for choice in FLIGHT_CLASS_CHOICES])
    days_in_location = serializers.IntegerField(min_value=1)
    accommodation_type = serializers.CharField()
    people_in_room = serializers.IntegerField(min_value=1)
    meal_type = serializers.ChoiceField(choices=[choice[0] for choice in MEAL_TYPE_CHOICES])
    meals_per_day = serializers.IntegerField(min_value=1, max_value=6)
    waste_management = serializers.ChoiceField(choices=[choice[0] for choice in TOURIST_WASTE_CHOICES])
    local_transport_choices = serializers.PrimaryKeyRelatedField(
        queryset=TransportType.objects.filter(is_active=True),
        many=True,
        required=False,
    )
    tours = serializers.ListField(child=serializers.IntegerField(), required=False)
    boat_trip_duration = serializers.ChoiceField(
        choices=[choice[0] for choice in BOAT_DURATION_CHOICES],
        required=False,
        allow_blank=True,
        default="none",
    )
    helicopter_ride_duration = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    helicopter_ride_passengers = serializers.IntegerField(required=False, min_value=1, allow_null=True)

    def validate_accommodation_type(self, value):
        valid_codes = {choice[0] for choice in ACCOMMODATION_TYPE_CHOICES}
        if value not in valid_codes:
            raise serializers.ValidationError("Тип проживания задан неверно.")
        return value

    def validate(self, attrs):
        transport_codes = {item.code for item in attrs.get("local_transport_choices", []) if item.code}
        if "helicopter" in transport_codes:
            if not attrs.get("helicopter_ride_duration"):
                raise serializers.ValidationError(
                    {"helicopter_ride_duration": "Укажите длительность вертолетной экскурсии."}
                )
            if not attrs.get("helicopter_ride_passengers"):
                raise serializers.ValidationError(
                    {"helicopter_ride_passengers": "Укажите количество пассажиров."}
                )
        if "boat" in transport_codes and attrs.get("boat_trip_duration", "none") == "none":
            raise serializers.ValidationError({"boat_trip_duration": "Укажите продолжительность прогулки."})
        return attrs


class LocalSurveySerializer(serializers.Serializer):
    age = serializers.IntegerField(min_value=0, max_value=120)
    housing_type = serializers.ChoiceField(choices=[choice[0] for choice in HOUSING_TYPE_CHOICES])
    housing_area = serializers.IntegerField(min_value=1)
    people_in_home = serializers.IntegerField(min_value=1)
    heating_source = serializers.ChoiceField(choices=[choice[0] for choice in HEATING_SOURCE_CHOICES])
    personal_transport = serializers.ChoiceField(choices=[choice[0] for choice in PERSONAL_TRANSPORT_CHOICES])
    fuel_type = serializers.ChoiceField(choices=[choice[0] for choice in FUEL_TYPE_CHOICES])
    average_mileage_per_month = serializers.IntegerField(min_value=0)
    public_transport_usage = serializers.ChoiceField(
        choices=[choice[0] for choice in PUBLIC_TRANSPORT_USAGE_CHOICES]
    )
    flights_in_last_year = serializers.ChoiceField(choices=[choice[0] for choice in FLIGHT_SCOPE_CHOICES])
    flights_per_year = serializers.IntegerField(min_value=0)
    flight_type = serializers.ChoiceField(choices=[choice[0] for choice in FLIGHT_CLASS_CHOICES])
    waste_management = serializers.ChoiceField(choices=[choice[0] for choice in LOCAL_WASTE_CHOICES])

    def validate(self, attrs):
        if attrs["personal_transport"] == "none":
            attrs["fuel_type"] = "none"
            attrs["average_mileage_per_month"] = 0
        elif attrs["fuel_type"] == "none":
            raise serializers.ValidationError({"fuel_type": "Укажите тип топлива."})

        if attrs["flights_in_last_year"] == "none":
            attrs["flights_per_year"] = 0
            attrs["flight_type"] = "economy"
        elif attrs["flights_per_year"] <= 0:
            raise serializers.ValidationError({"flights_per_year": "Укажите количество перелетов за год."})
        return attrs


class CalculationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculationResult
        fields = (
            "id",
            "source",
            "user_type",
            "route",
            "answers",
            "breakdown",
            "total_emission",
            "recommendation_codes",
            "recommendation_text",
            "report",
            "created_at",
        )
