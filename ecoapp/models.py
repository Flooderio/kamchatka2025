from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


USER_TYPE_CHOICES = (
    ("tourist", "Турист"),
    ("local", "Местный житель"),
)

SOURCE_CHOICES = (
    ("web", "Веб-сайт"),
    ("telegram", "Telegram"),
)

FLIGHT_CLASS_CHOICES = (
    ("economy", "Эконом"),
    ("business", "Бизнес"),
)

ACCOMMODATION_TYPE_CHOICES = (
    ("hotel", "Отель"),
    ("glamping", "Глэмпинг"),
    ("guest_house", "Гостевой дом"),
    ("eco_lodge", "Эко-лодж"),
    ("tent", "Палатка"),
)

MEAL_TYPE_CHOICES = (
    ("standard", "Стандартное"),
    ("vegetarian", "Вегетарианское"),
    ("local", "Локальные продукты"),
)

TOURIST_WASTE_CHOICES = (
    ("one_bin", "Выбрасываю все вместе"),
    ("minimize", "Минимизирую отходы"),
    ("sort", "Сортирую отходы"),
)

LOCAL_WASTE_CHOICES = (
    ("no_sorting", "Без сортировки"),
    ("separate_collection", "Раздельный сбор"),
    ("composting", "Компостирование"),
)

HOUSING_TYPE_CHOICES = (
    ("apartment", "Квартира"),
    ("house", "Частный дом"),
)

HEATING_SOURCE_CHOICES = (
    ("central", "Центральное"),
    ("gas", "Газ"),
    ("electric", "Электричество"),
    ("wood", "Дрова"),
    ("coal", "Уголь"),
)

PERSONAL_TRANSPORT_CHOICES = (
    ("none", "Нет личного транспорта"),
    ("car", "Легковой автомобиль"),
    ("jeep", "Внедорожник"),
    ("minivan", "Микроавтобус"),
)

FUEL_TYPE_CHOICES = (
    ("none", "Нет личного транспорта"),
    ("gasoline", "Бензин"),
    ("diesel", "Дизель"),
    ("gas", "Газ"),
    ("electric", "Электричество"),
    ("hybrid", "Гибрид"),
)

PUBLIC_TRANSPORT_USAGE_CHOICES = (
    ("daily", "Ежедневно"),
    ("1_3_per_week", "1-3 раза в неделю"),
    ("rarely", "Редко"),
)

FLIGHT_SCOPE_CHOICES = (
    ("none", "Не летаю"),
    ("domestic", "Внутренние перелеты"),
    ("international", "Международные перелеты"),
)

BOAT_DURATION_CHOICES = (
    ("none", "Не использовал"),
    ("3_5h", "3-5 часов"),
    ("10_11h_8", "10-11 часов, катер до 8 мест"),
    ("10_11h_20", "10-11 часов, катер до 20 мест"),
)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class SurveyUser(TimestampedModel):
    session_key = models.CharField(max_length=40, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.user:
            identifier = self.user.username
        elif self.session_key:
            identifier = f"session:{self.session_key[:8]}"
        else:
            identifier = f"user:{self.pk}"
        suffix = self.user_type or "unknown"
        return f"{identifier} ({suffix})"


class TransportActivity(TimestampedModel):
    code = models.SlugField(max_length=64, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TransportType(TimestampedModel):
    code = models.SlugField(max_length=64, unique=True, null=True, blank=True)
    type_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("type_name",)

    def __str__(self):
        return self.type_name


class Route(TimestampedModel):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    default_duration_days = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    transport_modes = models.ManyToManyField(TransportType, blank=True, related_name="routes")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tour(TimestampedModel):
    code = models.SlugField(max_length=64, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    transport_choices = models.ManyToManyField(TransportType, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TransportOption(TimestampedModel):
    transport = models.ForeignKey(TransportType, on_delete=models.CASCADE)
    activity = models.ForeignKey(TransportActivity, on_delete=models.CASCADE, null=True, blank=True)
    survey_tourist = models.ForeignKey(
        "SurveyTourist",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transport_options",
    )
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        activity_name = self.activity.name if self.activity else "Без активности"
        return f"{activity_name} - {self.transport.type_name}"


class City(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    lat = models.FloatField()
    lon = models.FloatField()
    region_name = models.CharField(max_length=100, blank=True)
    region_iso_code = models.CharField(max_length=20, blank=True)
    federal_district = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class FactorSet(TimestampedModel):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=32, default="draft-v1")
    is_active = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    source = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("-created_at", "name")

    def __str__(self):
        return f"{self.name} ({self.version})"


class EmissionFactor(TimestampedModel):
    factor_set = models.ForeignKey(FactorSet, on_delete=models.CASCADE, related_name="factors")
    category = models.CharField(max_length=64)
    subtype = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=64)
    value = models.FloatField()
    source = models.CharField(max_length=255, blank=True)
    is_temporary = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("factor_set", "category", "subtype")
        ordering = ("category", "subtype")

    def __str__(self):
        return f"{self.factor_set.code}:{self.category}:{self.subtype}"


class Recommendation(TimestampedModel):
    code = models.SlugField(max_length=64, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True)
    trigger_category = models.CharField(max_length=64, blank=True)
    min_total_emission = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return self.title


class Checklist(TimestampedModel):
    code = models.SlugField(max_length=64, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class SurveyTourist(TimestampedModel):
    user = models.ForeignKey(SurveyUser, on_delete=models.CASCADE, related_name="tourist_surveys")
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    departure_city = models.ForeignKey(City, on_delete=models.CASCADE)
    is_transfer_in_moscow = models.BooleanField(default=False)
    flight_class = models.CharField(max_length=50, choices=FLIGHT_CLASS_CHOICES)
    days_in_location = models.IntegerField()
    accommodation_type = models.CharField(max_length=100, choices=ACCOMMODATION_TYPE_CHOICES)
    people_in_room = models.IntegerField()
    meal_type = models.CharField(max_length=50, choices=MEAL_TYPE_CHOICES)
    meals_per_day = models.IntegerField()
    waste_management = models.CharField(max_length=255, choices=TOURIST_WASTE_CHOICES)
    transport_choices = models.ManyToManyField(TransportType, blank=True)
    tours = models.ManyToManyField(Tour, blank=True)
    boat_trip_duration = models.CharField(max_length=100, choices=BOAT_DURATION_CHOICES, default="none", blank=True)
    helicopter_ride_duration = models.IntegerField(null=True, blank=True)
    helicopter_ride_passengers = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Опрос туриста #{self.pk}"


class SurveyLocal(TimestampedModel):
    user = models.ForeignKey(SurveyUser, on_delete=models.CASCADE, related_name="local_surveys")
    housing_type = models.CharField(max_length=100, choices=HOUSING_TYPE_CHOICES)
    people_in_home = models.IntegerField()
    housing_area = models.IntegerField()
    heating_source = models.CharField(max_length=100, choices=HEATING_SOURCE_CHOICES)
    personal_transport = models.CharField(max_length=100, choices=PERSONAL_TRANSPORT_CHOICES)
    fuel_type = models.CharField(max_length=50, choices=FUEL_TYPE_CHOICES)
    average_mileage_per_month = models.IntegerField()
    public_transport_usage = models.CharField(max_length=100, choices=PUBLIC_TRANSPORT_USAGE_CHOICES)
    flights_in_last_year = models.CharField(max_length=100, choices=FLIGHT_SCOPE_CHOICES)
    flights_per_year = models.PositiveIntegerField(default=0)
    flight_type = models.CharField(max_length=100, choices=FLIGHT_CLASS_CHOICES, default="economy")
    waste_management = models.CharField(max_length=100, choices=LOCAL_WASTE_CHOICES)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Опрос местного жителя #{self.pk}"


class CalculationResult(TimestampedModel):
    anonymized_user_id = models.CharField(max_length=128, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    factor_set = models.ForeignKey(FactorSet, on_delete=models.SET_NULL, null=True, blank=True)
    checklist = models.ForeignKey(Checklist, on_delete=models.SET_NULL, null=True, blank=True)
    answers = models.JSONField(default=dict)
    breakdown = models.JSONField(default=dict)
    total_emission = models.FloatField()
    recommendation_codes = models.JSONField(default=list, blank=True)
    recommendation_text = models.TextField(blank=True)
    report = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user_type}:{self.source}:{self.total_emission:.2f} кг CO2e"
    