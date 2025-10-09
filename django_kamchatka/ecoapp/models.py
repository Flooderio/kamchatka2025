from django.db import models
from django.contrib.auth.models import User

    
# Модель для пользователя
class SurveyUser(models.Model):
    USER_TYPES = (
        ('tourist', 'Турист'),
        ('local', 'Местный'),
    )
    session_key = models.CharField(max_length=40, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(max_length=7, choices=USER_TYPES)
    age = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.user_type})"
    
    
# Транспорт и активность
class TransportActivity(models.Model):
    name = models.CharField(max_length=255)  # Название активности или локации

    def __str__(self):
        return self.name


# Тип транспорта
class TransportType(models.Model):
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return self.type_name



# Модель экскурсии
class Tour(models.Model):
    name = models.CharField(max_length=255)  # Название экскурсии
    description = models.TextField(blank=True, null=True)  # Описание экскурсии (по желанию)
    transport_choices = models.ManyToManyField(TransportType, blank=True)  # Связь с транспортом

    def __str__(self):
        return self.name



class TransportOption(models.Model):
    transport = models.ForeignKey(TransportType, on_delete=models.CASCADE)
    activity = models.ForeignKey(TransportActivity, on_delete=models.CASCADE,  null=True)
    survey_tourist = models.ForeignKey('SurveyTourist', on_delete=models.CASCADE, null=True, blank=True, related_name='transport_options')

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return f"{self.survey_tourist}: {self.activity.name} - {self.transport.name}"


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    lat = models.FloatField()  
    lon = models.FloatField()  
    region_name = models.CharField(max_length=100, blank=True)  
    region_iso_code = models.CharField(max_length=20, blank=True) 
    federal_district = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class SurveyTourist(models.Model):
    user = models.OneToOneField(SurveyUser, on_delete=models.CASCADE)
    departure_city = models.ForeignKey(City, on_delete=models.CASCADE)
    is_transfer_in_moscow = models.BooleanField(default=False)
    flight_class = models.CharField(max_length=50, choices=[('economy', 'Эконом'), ('business', 'Бизнес')])
    days_in_location = models.IntegerField()
    accommodation_type = models.CharField(max_length=100, choices=[('hotel', 'Благоустроенное жильё (отель/глэмпинг/гостевой дом)'), ('tent', 'Палатка')])
    people_in_room = models.IntegerField()
    meal_type = models.CharField(max_length=50, choices=[('standard', 'Стандартное'), ('vegetarian', 'Вегетарианское')])
    meals_per_day = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3')])
    waste_management = models.CharField(max_length=255, choices=[
        ('one_bin', 'Выбрасываю всё вместе в один бак'),
        ('minimize', 'Минимизирую образование отходов'),
        ('sort', 'Разделяю по видам')
    ])

    transport_choices = models.ManyToManyField(TransportType, blank=True)
    boat_trip_duration = models.CharField(max_length=100, choices=[('3-5h', '3-5 часов'), ('10-11h_8', '10-11 часов (катер до 8 мест)'), ('10-11h_20', '10-11 часов (катер до 20 мест)')])
    helicopter_ride_duration = models.IntegerField(null=True, blank=True)
    helicopter_ride_passengers = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Опрос туриста для {self.user}"


# Опрос для местных жителей
class SurveyLocal(models.Model):
    user = models.OneToOneField(SurveyUser, on_delete=models.CASCADE)
    housing_type = models.CharField(max_length=100, choices=[
        ('apartment', 'Квартира'),
        ('house', 'Частный дом')
    ])
    people_in_home = models.IntegerField()
    housing_area = models.IntegerField()
    heating_source = models.CharField(max_length=100, choices=[
        ('central', 'Центральное'),
        ('gas', 'Газ'),
        ('electric', 'Электричество'),
        ('wood', 'Дрова'),
        ('coal', 'Уголь')
    ])
    personal_transport = models.CharField(max_length=100, choices=[
        ('car', 'Легковой автомобиль'),
        ('jeep', 'Джип'),
        ('minivan', 'Минивен'),
        ('none', 'Нет личного транспорта')
    ])
    fuel_type = models.CharField(max_length=50, choices=[
        ('gasoline', 'Бензин'),
        ('diesel', 'Дизель'),
        ('gas', 'Газ'),
        ('electric', 'Электро'),
        ('hybrid', 'Гибрид'),
        ('none', 'Нет личного транспорта')
    ])
    average_mileage_per_month = models.IntegerField()
    public_transport_usage = models.CharField(max_length=100, choices=[
        ('daily', 'Ежедневно'),
        ('1-3_per_week', '1-3 раза в неделю'),
        ('rarely', 'Очень редко')
    ])
    flights_in_last_year = models.CharField(max_length=100, choices=[
        ('domestic', 'Внутренний'),
        ('international', 'Международный'),
        ('none', 'Не летал самолетом')
    ])
    flight_type = models.CharField(max_length=100, choices=[
        ('economy', 'Эконом'),
        ('business', 'Бизнес'),
        ('first_class', 'Первый класс'),
        ('none', 'Не летал самолетом')
    ])
    waste_management = models.CharField(max_length=100, choices=[
        ('no_sorting', 'Без сортировки'),
        ('separate_collection', 'Раздельный сбор'),
        ('composting', 'Компостирование')
    ])

    def __str__(self):
        return f"Опрос местного жителя для {self.user}"
    