from django import forms

from .models import (
    ACCOMMODATION_TYPE_CHOICES,
    BOAT_DURATION_CHOICES,
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
    City,
    Route,
    Tour,
    TransportType,
)


class SurveyTouristForm(forms.Form):
    age = forms.IntegerField(min_value=0, max_value=120, label="Возраст")
    route = forms.ModelChoiceField(queryset=Route.objects.none(), label="Маршрут")
    departure_city = forms.ModelChoiceField(queryset=City.objects.none(), label="Город отправления")
    is_transfer_in_moscow = forms.TypedChoiceField(
        choices=((True, "Да"), (False, "Нет")),
        coerce=lambda value: str(value).lower() in {"true", "1", "yes"},
        widget=forms.RadioSelect,
        label="Есть пересадка в Москве",
    )
    flight_class = forms.ChoiceField(choices=FLIGHT_CLASS_CHOICES, label="Класс перелета")
    days_in_location = forms.IntegerField(min_value=1, label="Количество дней")
    accommodation_type = forms.ChoiceField(choices=ACCOMMODATION_TYPE_CHOICES, label="Тип проживания")
    people_in_room = forms.IntegerField(min_value=1, label="Людей в размещении")
    meal_type = forms.ChoiceField(choices=MEAL_TYPE_CHOICES, label="Тип питания")
    meals_per_day = forms.IntegerField(min_value=1, max_value=6, label="Приемов пищи в день")
    waste_management = forms.ChoiceField(choices=TOURIST_WASTE_CHOICES, label="Обращение с отходами")
    tours = forms.ModelMultipleChoiceField(
        queryset=Tour.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Экскурсии",
    )
    local_transport_choices = forms.ModelMultipleChoiceField(
        queryset=TransportType.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Локальный транспорт",
    )
    boat_trip_duration = forms.ChoiceField(
        choices=BOAT_DURATION_CHOICES,
        required=False,
        label="Катер",
    )
    helicopter_ride_duration = forms.IntegerField(
        required=False,
        min_value=0,
        label="Длительность вертолетной экскурсии, мин",
    )
    helicopter_ride_passengers = forms.IntegerField(
        required=False,
        min_value=1,
        label="Количество пассажиров на борту",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["route"].queryset = Route.objects.filter(is_active=True)
        self.fields["departure_city"].queryset = City.objects.all()
        self.fields["tours"].queryset = Tour.objects.filter(is_active=True)
        self.fields["local_transport_choices"].queryset = TransportType.objects.filter(is_active=True)

        route = None
        route_id = self.data.get("route") or self.initial.get("route")
        if route_id:
            try:
                route = Route.objects.prefetch_related("transport_modes").get(pk=route_id)
            except (Route.DoesNotExist, ValueError, TypeError):
                route = None
        if route:
            self.fields["local_transport_choices"].queryset = route.transport_modes.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        selected_transport_codes = {
            transport.code for transport in cleaned_data.get("local_transport_choices", []) if transport.code
        }
        boat_duration = cleaned_data.get("boat_trip_duration") or "none"

        if "helicopter" in selected_transport_codes:
            if not cleaned_data.get("helicopter_ride_duration"):
                self.add_error(
                    "helicopter_ride_duration",
                    "Укажите длительность вертолетной экскурсии.",
                )
            if not cleaned_data.get("helicopter_ride_passengers"):
                self.add_error(
                    "helicopter_ride_passengers",
                    "Укажите количество пассажиров на вертолете.",
                )
        if "boat" in selected_transport_codes and boat_duration == "none":
            self.add_error("boat_trip_duration", "Укажите продолжительность прогулки на катере.")
        return cleaned_data


class SurveyLocalForm(forms.Form):
    age = forms.IntegerField(min_value=0, max_value=120, label="Возраст")
    housing_type = forms.ChoiceField(choices=HOUSING_TYPE_CHOICES, label="Тип жилья")
    housing_area = forms.IntegerField(min_value=1, label="Площадь жилья, м2")
    people_in_home = forms.IntegerField(min_value=1, label="Количество проживающих")
    heating_source = forms.ChoiceField(choices=HEATING_SOURCE_CHOICES, label="Источник отопления")
    personal_transport = forms.ChoiceField(
        choices=PERSONAL_TRANSPORT_CHOICES,
        label="Личный транспорт",
    )
    fuel_type = forms.ChoiceField(choices=FUEL_TYPE_CHOICES, label="Тип топлива")
    average_mileage_per_month = forms.IntegerField(min_value=0, label="Пробег в месяц, км")
    public_transport_usage = forms.ChoiceField(
        choices=PUBLIC_TRANSPORT_USAGE_CHOICES,
        label="Использование общественного транспорта",
    )
    flights_in_last_year = forms.ChoiceField(choices=FLIGHT_SCOPE_CHOICES, label="Тип перелетов")
    flights_per_year = forms.IntegerField(min_value=0, label="Количество перелетов за год")
    flight_type = forms.ChoiceField(choices=FLIGHT_CLASS_CHOICES, label="Класс перелета")
    waste_management = forms.ChoiceField(choices=LOCAL_WASTE_CHOICES, label="Обращение с отходами")

    def clean(self):
        cleaned_data = super().clean()
        personal_transport = cleaned_data.get("personal_transport")
        fuel_type = cleaned_data.get("fuel_type")
        mileage = cleaned_data.get("average_mileage_per_month") or 0
        flights_scope = cleaned_data.get("flights_in_last_year")
        flights_per_year = cleaned_data.get("flights_per_year") or 0

        if personal_transport == "none":
            cleaned_data["fuel_type"] = "none"
            cleaned_data["average_mileage_per_month"] = 0
        elif fuel_type == "none":
            self.add_error("fuel_type", "Укажите тип топлива для личного транспорта.")

        if personal_transport != "none" and mileage <= 0:
            self.add_error("average_mileage_per_month", "Укажите пробег больше нуля.")

        if flights_scope == "none":
            cleaned_data["flights_per_year"] = 0
            cleaned_data["flight_type"] = "economy"
        elif flights_per_year <= 0:
            self.add_error("flights_per_year", "Укажите количество перелетов за год.")

        return cleaned_data

