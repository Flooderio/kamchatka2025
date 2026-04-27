from django.core.management.base import BaseCommand

from ecoapp.models import (
    Checklist,
    City,
    EmissionFactor,
    FactorSet,
    Recommendation,
    Route,
    Tour,
    TransportType,
)


class Command(BaseCommand):
    help = "Заполняет стартовые справочники маршрутов, транспорта, коэффициентов и рекомендаций."

    def handle(self, *args, **options):
        transport_types = [
            ("shift_worker", "Вахтовик"),
            ("jeep", "Внедорожник"),
            ("minivan", "Микроавтобус"),
            ("helicopter", "Вертолет"),
            ("boat", "Катер"),
        ]
        created_transports = {}
        for code, name in transport_types:
            created_transports[code], _ = TransportType.objects.update_or_create(
                code=code,
                defaults={"type_name": name, "is_active": True},
            )

        routes = [
            ("avacha", "Авачинский перевал", "Классический маршрут к подножию вулканов", 3, ["jeep", "minivan"]),
            ("mutnovsky", "Мутновский вулкан", "Однодневный маршрут к кратеру и фумаролам", 2, ["jeep", "minivan"]),
            ("gorely", "Горелый вулкан", "Треккинговый маршрут к кратеру Горелого", 2, ["jeep"]),
            ("kuril_lake", "Курильское озеро", "Наблюдение за медведями и природой", 3, ["helicopter", "boat"]),
            ("nalychevo", "Налычевская долина", "Термальные источники и пеший маршрут", 4, ["minivan"]),
            ("tolbachik", "Толбачик", "Дальний вулканический маршрут", 5, ["shift_worker", "jeep"]),
            ("klyuchevskaya", "Ключевская группа вулканов", "Экспедиционный маршрут по центральной Камчатке", 7, ["shift_worker"]),
            ("bystrinsky", "Быстринский парк", "Культурно-природный маршрут", 4, ["minivan"]),
            ("vachkazhets", "Вачкажец", "Пеший маршрут по горному массиву", 2, ["jeep"]),
            ("halaktyrsky", "Халактырский пляж", "Прибрежный маршрут и океан", 1, ["jeep", "minivan"]),
            ("zhupanovo", "Бухта Жупанова", "Морской маршрут", 2, ["boat"]),
            ("paramushir_view", "Северные панорамы", "Комбинированный маршрут по северу", 5, ["minivan", "helicopter"]),
            ("south_kamchatka", "Южно-Камчатский кластер", "Маршрут по южным природным объектам", 6, ["jeep", "boat"]),
        ]
        for code, name, description, duration, transport_codes in routes:
            route, _ = Route.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "default_duration_days": duration,
                    "is_active": True,
                },
            )
            route.transport_modes.set([created_transports[item] for item in transport_codes])

        tours = [
            ("avacha_tour", "Экскурсия на Авачинский перевал", "Внедорожный выезд"),
            ("kuril_boat", "Морская прогулка к бухтам", "Катерный маршрут"),
            ("valley_heli", "Вертолетная экскурсия", "Обзорная экскурсия с воздуха"),
        ]
        for code, name, description in tours:
            tour, _ = Tour.objects.update_or_create(
                code=code,
                defaults={"name": name, "description": description, "is_active": True},
            )
            if code == "kuril_boat":
                tour.transport_choices.set([created_transports["boat"]])
            elif code == "valley_heli":
                tour.transport_choices.set([created_transports["helicopter"]])
            else:
                tour.transport_choices.set([created_transports["jeep"]])

        city_rows = [
            ("Петропавловск-Камчатский", 53.0452, 158.6483, "Камчатский край"),
            ("Москва", 55.7558, 37.6173, "Москва"),
            ("Санкт-Петербург", 59.9311, 30.3609, "Санкт-Петербург"),
            ("Новосибирск", 55.0084, 82.9357, "Новосибирская область"),
            ("Владивосток", 43.1155, 131.8855, "Приморский край"),
        ]
        for name, lat, lon, region in city_rows:
            City.objects.update_or_create(
                name=name,
                defaults={
                    "lat": lat,
                    "lon": lon,
                    "region_name": region,
                    "region_iso_code": "",
                    "federal_district": "",
                },
            )

        factor_set, _ = FactorSet.objects.update_or_create(
            code="draft_v1",
            defaults={
                "name": "Draft factors",
                "description": "Стартовый набор коэффициентов для первого прохода.",
                "version": "draft-v1",
                "is_active": True,
                "is_draft": True,
                "source": "Project assumptions / open sources",
            },
        )

        factors = [
            ("flight", "economy", "Авиаперелет эконом", "kg_co2e_per_km", 0.133),
            ("flight", "business", "Авиаперелет бизнес", "kg_co2e_per_km", 0.255),
            ("flight_modifier", "transfer_moscow", "Пересадка в Москве", "multiplier", 1.15),
            ("accommodation", "hotel", "Отель", "kg_co2e_per_day", 20.0),
            ("accommodation", "glamping", "Глэмпинг", "kg_co2e_per_day", 16.0),
            ("accommodation", "guest_house", "Гостевой дом", "kg_co2e_per_day", 12.0),
            ("accommodation", "eco_lodge", "Эко-лодж", "kg_co2e_per_day", 8.0),
            ("accommodation", "tent", "Палатка", "kg_co2e_per_day", 2.0),
            ("meal", "standard", "Стандартное питание", "kg_co2e_per_meal", 2.4),
            ("meal", "vegetarian", "Вегетарианское питание", "kg_co2e_per_meal", 1.4),
            ("meal", "local", "Локальные продукты", "kg_co2e_per_meal", 1.9),
            ("tourist_waste", "one_bin", "Без сортировки", "kg_co2e_per_day", 0.7),
            ("tourist_waste", "minimize", "Минимизация отходов", "kg_co2e_per_day", 0.3),
            ("tourist_waste", "sort", "Сортировка", "kg_co2e_per_day", 0.15),
            ("local_transport", "shift_worker", "Вахтовик", "kg_co2e_per_day", 18.0),
            ("local_transport", "jeep", "Внедорожник", "kg_co2e_per_day", 25.0),
            ("local_transport", "minivan", "Микроавтобус", "kg_co2e_per_day", 14.0),
            ("local_transport", "helicopter", "Вертолет", "kg_co2e_per_hour", 150.0),
            ("boat", "3_5h", "Катер 3-5 часов", "kg_co2e_per_trip", 45.0),
            ("boat", "10_11h_8", "Катер 10-11 часов до 8 мест", "kg_co2e_per_trip", 95.0),
            ("boat", "10_11h_20", "Катер 10-11 часов до 20 мест", "kg_co2e_per_trip", 120.0),
            ("housing_base", "apartment", "Квартира", "kg_co2e_per_m2_per_month", 0.8),
            ("housing_base", "house", "Частный дом", "kg_co2e_per_m2_per_month", 1.2),
            ("heating", "central", "Центральное отопление", "kg_co2e_per_m2_per_month", 0.5),
            ("heating", "gas", "Газовое отопление", "kg_co2e_per_m2_per_month", 0.45),
            ("heating", "electric", "Электрическое отопление", "kg_co2e_per_m2_per_month", 0.6),
            ("heating", "wood", "Дрова", "kg_co2e_per_m2_per_month", 0.35),
            ("heating", "coal", "Уголь", "kg_co2e_per_m2_per_month", 0.8),
            ("fuel", "gasoline", "Бензин", "kg_co2e_per_km", 0.192),
            ("fuel", "diesel", "Дизель", "kg_co2e_per_km", 0.171),
            ("fuel", "gas", "Газ", "kg_co2e_per_km", 0.14),
            ("fuel", "electric", "Электротранспорт", "kg_co2e_per_km", 0.07),
            ("fuel", "hybrid", "Гибрид", "kg_co2e_per_km", 0.11),
            ("vehicle_multiplier", "car", "Легковой автомобиль", "multiplier", 1.0),
            ("vehicle_multiplier", "jeep", "Внедорожник", "multiplier", 1.25),
            ("vehicle_multiplier", "minivan", "Микроавтобус", "multiplier", 1.18),
            ("public_transport", "daily", "Ежедневное использование", "kg_co2e_per_year", 180.0),
            ("public_transport", "1_3_per_week", "1-3 раза в неделю", "kg_co2e_per_year", 95.0),
            ("public_transport", "rarely", "Редкое использование", "kg_co2e_per_year", 35.0),
            ("annual_flight", "domestic_economy", "Внутренний перелет эконом", "kg_co2e_per_flight", 290.0),
            ("annual_flight", "domestic_business", "Внутренний перелет бизнес", "kg_co2e_per_flight", 420.0),
            ("annual_flight", "international_economy", "Международный перелет эконом", "kg_co2e_per_flight", 680.0),
            ("annual_flight", "international_business", "Международный перелет бизнес", "kg_co2e_per_flight", 980.0),
            ("local_waste", "no_sorting", "Без сортировки", "kg_co2e_per_year", 80.0),
            ("local_waste", "separate_collection", "Раздельный сбор", "kg_co2e_per_year", 45.0),
            ("local_waste", "composting", "Компостирование", "kg_co2e_per_year", 20.0),
        ]
        for category, subtype, name, unit, value in factors:
            EmissionFactor.objects.update_or_create(
                factor_set=factor_set,
                category=category,
                subtype=subtype,
                defaults={
                    "name": name,
                    "unit": unit,
                    "value": value,
                    "source": "Draft baseline",
                    "is_temporary": True,
                },
            )

        recommendations = [
            ("tourist_flight", "tourist", "flight", 500, "Снизьте авиационный след", "По возможности выбирайте более длинные поездки вместо частых коротких вылетов."),
            ("tourist_transport", "tourist", "local_transport", 300, "Сократите локальный транспорт", "Объединяйте экскурсии и выбирайте групповой транспорт по маршруту."),
            ("local_housing", "local", "housing", 1000, "Повышайте энергоэффективность жилья", "Проверьте утепление, окна и режим отопления."),
            ("local_transport", "local", "personal_transport", 800, "Снижайте автомобильный след", "Сократите пробег и объединяйте поездки."),
            ("common_food", "", "meals", 0, "Переходите на локальные продукты", "Локальные и растительные блюда обычно снижают углеродный след."),
        ]
        for code, user_type, category, threshold, title, content in recommendations:
            Recommendation.objects.update_or_create(
                code=code,
                defaults={
                    "user_type": user_type,
                    "trigger_category": category,
                    "min_total_emission": threshold,
                    "title": title,
                    "content": content,
                    "is_active": True,
                },
            )

        Checklist.objects.update_or_create(
            code="tourist_default",
            defaults={
                "user_type": "tourist",
                "title": "Чек-лист туриста",
                "content": "Берите многоразовую бутылку, объединяйте экскурсии, выбирайте локальную еду и групповой транспорт.",
                "url": "",
                "is_active": True,
            },
        )
        Checklist.objects.update_or_create(
            code="local_default",
            defaults={
                "user_type": "local",
                "title": "Чек-лист местного жителя",
                "content": "Следите за утеплением жилья, пробегом автомобиля, сортировкой отходов и частотой перелетов.",
                "url": "",
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Reference data seeded successfully."))
