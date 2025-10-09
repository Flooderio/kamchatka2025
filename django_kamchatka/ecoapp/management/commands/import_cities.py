import csv
from django.core.management.base import BaseCommand
from ecoapp.models import City  # Убедитесь, что импортируете вашу модель City
import os

class Command(BaseCommand):
    help = 'Загружает города с координатами из CSV файла'

    def handle(self, *args, **kwargs):
        # Получаем текущую директорию, где выполняется скрипт, и формируем путь к CSV файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'cities.csv')

        # Открываем CSV файл
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)  # Чтение CSV как словаря (ключ = название столбца)

            # Собираем все строки в список
            cities = []
            for row in reader:
                city_name = row['city'].strip()  # Название города
                lat = float(row['lat'])  # Широта
                lon = float(row['lon'])  # Долгота
                region_name = row['region_name'].strip()  # Регион
                region_iso_code = row['region_iso_code'].strip()  # Код региона
                federal_district = row['federal_district'].strip()  # Федеральный округ

                # Добавляем строку в список
                cities.append({
                    'name': city_name,
                    'lat': lat,
                    'lon': lon,
                    'region_name': region_name,
                    'region_iso_code': region_iso_code,
                    'federal_district': federal_district
                })

            # Сортируем список по имени города
            cities.sort(key=lambda x: x['name'])

            # Чтение строк из списка и импорт данных в базу
            for city in cities:
                # Проверяем, существует ли город в базе, если нет — создаём новый
                if not City.objects.filter(name=city['name']).exists():
                    City.objects.create(
                        name=city['name'],
                        lat=city['lat'],
                        lon=city['lon'],
                        region_name=city['region_name'],
                        region_iso_code=city['region_iso_code'],
                        federal_district=city['federal_district']
                    )

            # Выводим сообщение в случае успешной загрузки
            self.stdout.write(self.style.SUCCESS('Города успешно загружены!'))
