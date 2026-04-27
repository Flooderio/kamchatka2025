from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from ecoapp.bot.keyboards import options_keyboard
from ecoapp.bot.messages import WELCOME_MESSAGE
from ecoapp.bot.states import LocalSurveyStates, TouristSurveyStates
from ecoapp.models import (
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
    TransportType,
)
from ecoapp.services.calculation import calculate_survey
from ecoapp.services.persistence import get_or_create_survey_user, persist_calculation_result
from ecoapp.services.recommendations import get_recommendations_for_outcome

router = Router()


def choice_map(choices) -> dict[str, str]:
    return {label: code for code, label in choices}


def labels(choices) -> list[str]:
    return [label for _, label in choices]


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_MESSAGE, reply_markup=options_keyboard(["Турист", "Местный житель"]))


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Опрос отменен.", reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(None), F.text.in_(["Турист", "Местный житель"]))
async def scenario_handler(message: Message, state: FSMContext):
    if message.text == "Турист":
        routes = list(Route.objects.filter(is_active=True).order_by("name"))
        await state.update_data(route_options={route.name: route.pk for route in routes})
        await state.set_state(TouristSurveyStates.route)
        await message.answer("Выберите маршрут.", reply_markup=options_keyboard([route.name for route in routes]))
        return

    await state.set_state(LocalSurveyStates.housing_type)
    await message.answer("Укажите тип жилья.", reply_markup=options_keyboard(labels(HOUSING_TYPE_CHOICES)))


@router.message(TouristSurveyStates.route)
async def tourist_route_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    route_id = data.get("route_options", {}).get(message.text)
    if not route_id:
        await message.answer("Выберите маршрут из списка.")
        return
    await state.update_data(route=route_id)
    cities = list(City.objects.order_by("name")[:25])
    await state.update_data(city_options={city.name: city.pk for city in cities})
    await state.set_state(TouristSurveyStates.departure_city)
    await message.answer("Укажите город отправления.", reply_markup=options_keyboard([city.name for city in cities]))


@router.message(TouristSurveyStates.departure_city)
async def tourist_city_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    city_id = data.get("city_options", {}).get(message.text)
    if not city_id:
        await message.answer("Выберите город из списка.")
        return
    await state.update_data(departure_city=city_id)
    await state.set_state(TouristSurveyStates.transfer)
    await message.answer("Есть пересадка в Москве?", reply_markup=options_keyboard(["Да", "Нет"]))


@router.message(TouristSurveyStates.transfer)
async def tourist_transfer_handler(message: Message, state: FSMContext):
    if message.text not in {"Да", "Нет"}:
        await message.answer("Выберите Да или Нет.")
        return
    await state.update_data(is_transfer_in_moscow=message.text == "Да")
    await state.set_state(TouristSurveyStates.flight_class)
    await message.answer("Выберите класс перелета.", reply_markup=options_keyboard(labels(FLIGHT_CLASS_CHOICES)))


@router.message(TouristSurveyStates.flight_class)
async def tourist_flight_class_handler(message: Message, state: FSMContext):
    value = choice_map(FLIGHT_CLASS_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите класс перелета из списка.")
        return
    await state.update_data(flight_class=value)
    await state.set_state(TouristSurveyStates.days)
    await message.answer("Сколько дней длится поездка?")


@router.message(TouristSurveyStates.days)
async def tourist_days_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Введите число дней больше нуля.")
        return
    await state.update_data(days_in_location=int(message.text))
    await state.set_state(TouristSurveyStates.accommodation)
    await message.answer("Выберите тип проживания.", reply_markup=options_keyboard(labels(ACCOMMODATION_TYPE_CHOICES)))


@router.message(TouristSurveyStates.accommodation)
async def tourist_accommodation_handler(message: Message, state: FSMContext):
    value = choice_map(ACCOMMODATION_TYPE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите тип проживания из списка.")
        return
    await state.update_data(accommodation_type=value)
    await state.set_state(TouristSurveyStates.people_in_room)
    await message.answer("Сколько человек размещается вместе с вами?")


@router.message(TouristSurveyStates.people_in_room)
async def tourist_people_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Введите число больше нуля.")
        return
    await state.update_data(people_in_room=int(message.text))
    await state.set_state(TouristSurveyStates.meal_type)
    await message.answer("Выберите тип питания.", reply_markup=options_keyboard(labels(MEAL_TYPE_CHOICES)))


@router.message(TouristSurveyStates.meal_type)
async def tourist_meal_handler(message: Message, state: FSMContext):
    value = choice_map(MEAL_TYPE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите тип питания из списка.")
        return
    await state.update_data(meal_type=value)
    await state.set_state(TouristSurveyStates.meals_per_day)
    await message.answer("Сколько полноценных приемов пищи в день?")


@router.message(TouristSurveyStates.meals_per_day)
async def tourist_meals_per_day_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or not 1 <= int(message.text) <= 6:
        await message.answer("Введите число от 1 до 6.")
        return
    await state.update_data(meals_per_day=int(message.text))
    await state.set_state(TouristSurveyStates.waste)
    await message.answer("Как вы обращаетесь с отходами?", reply_markup=options_keyboard(labels(TOURIST_WASTE_CHOICES)))


@router.message(TouristSurveyStates.waste)
async def tourist_waste_handler(message: Message, state: FSMContext):
    value = choice_map(TOURIST_WASTE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите вариант из списка.")
        return
    await state.update_data(waste_management=value)
    transports = list(TransportType.objects.filter(is_active=True).order_by("type_name"))
    transport_labels = [f"{item.type_name} ({item.code})" for item in transports]
    await state.update_data(transport_options={label: item.pk for label, item in zip(transport_labels, transports)})
    await state.set_state(TouristSurveyStates.local_transport)
    await message.answer(
        "Выберите локальный транспорт. Можно указать несколько вариантов через запятую, копируя названия из списка.",
        reply_markup=options_keyboard(transport_labels),
    )


@router.message(TouristSurveyStates.local_transport)
async def tourist_transport_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    options = data.get("transport_options", {})
    selected = []
    for chunk in [item.strip() for item in message.text.split(",") if item.strip()]:
        pk = options.get(chunk)
        if pk:
            selected.append(pk)
    if not selected and message.text.strip():
        await message.answer("Укажите транспорт из предложенного списка.")
        return
    await state.update_data(local_transport_choices=selected, tours=[], boat_trip_duration="none")
    selected_objects = list(TransportType.objects.filter(pk__in=selected))
    codes = {item.code for item in selected_objects if item.code}
    if "boat" in codes:
        await state.set_state(TouristSurveyStates.boat_duration)
        await message.answer("Укажите длительность прогулки на катере.", reply_markup=options_keyboard(labels(BOAT_DURATION_CHOICES)))
        return
    if "helicopter" in codes:
        await state.set_state(TouristSurveyStates.helicopter_duration)
        await message.answer("Введите длительность вертолетной экскурсии в минутах.")
        return
    await complete_tourist_flow(message, state)


@router.message(TouristSurveyStates.boat_duration)
async def tourist_boat_handler(message: Message, state: FSMContext):
    value = choice_map(BOAT_DURATION_CHOICES).get(message.text)
    if value is None:
        await message.answer("Выберите длительность из списка.")
        return
    await state.update_data(boat_trip_duration=value)
    data = await state.get_data()
    selected_objects = list(TransportType.objects.filter(pk__in=data.get("local_transport_choices", [])))
    codes = {item.code for item in selected_objects if item.code}
    if "helicopter" in codes:
        await state.set_state(TouristSurveyStates.helicopter_duration)
        await message.answer("Введите длительность вертолетной экскурсии в минутах.")
        return
    await complete_tourist_flow(message, state)


@router.message(TouristSurveyStates.helicopter_duration)
async def tourist_helicopter_duration_handler(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите длительность в минутах.")
        return
    await state.update_data(helicopter_ride_duration=int(message.text))
    await state.set_state(TouristSurveyStates.helicopter_passengers)
    await message.answer("Сколько пассажиров было на борту?")


@router.message(TouristSurveyStates.helicopter_passengers)
async def tourist_helicopter_passengers_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Введите количество пассажиров больше нуля.")
        return
    await state.update_data(helicopter_ride_passengers=int(message.text))
    await complete_tourist_flow(message, state)


async def complete_tourist_flow(message: Message, state: FSMContext):
    raw_data = await state.get_data()
    answers = {
        "age": 0,
        "route": Route.objects.get(pk=raw_data["route"]),
        "departure_city": City.objects.get(pk=raw_data["departure_city"]),
        "is_transfer_in_moscow": raw_data["is_transfer_in_moscow"],
        "flight_class": raw_data["flight_class"],
        "days_in_location": raw_data["days_in_location"],
        "accommodation_type": raw_data["accommodation_type"],
        "people_in_room": raw_data["people_in_room"],
        "meal_type": raw_data["meal_type"],
        "meals_per_day": raw_data["meals_per_day"],
        "waste_management": raw_data["waste_management"],
        "local_transport_choices": list(TransportType.objects.filter(pk__in=raw_data.get("local_transport_choices", []))),
        "tours": [],
        "boat_trip_duration": raw_data.get("boat_trip_duration", "none"),
        "helicopter_ride_duration": raw_data.get("helicopter_ride_duration"),
        "helicopter_ride_passengers": raw_data.get("helicopter_ride_passengers"),
    }
    result_text = save_and_render_result(message, "tourist", answers)
    await state.clear()
    await message.answer(result_text, reply_markup=ReplyKeyboardRemove())


@router.message(LocalSurveyStates.housing_type)
async def local_housing_type_handler(message: Message, state: FSMContext):
    value = choice_map(HOUSING_TYPE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите тип жилья из списка.")
        return
    await state.update_data(age=0, housing_type=value)
    await state.set_state(LocalSurveyStates.housing_area)
    await message.answer("Введите площадь жилья в м2.")


@router.message(LocalSurveyStates.housing_area)
async def local_housing_area_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Введите площадь больше нуля.")
        return
    await state.update_data(housing_area=int(message.text))
    await state.set_state(LocalSurveyStates.people_in_home)
    await message.answer("Сколько человек проживает в жилье?")


@router.message(LocalSurveyStates.people_in_home)
async def local_people_in_home_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Введите число больше нуля.")
        return
    await state.update_data(people_in_home=int(message.text))
    await state.set_state(LocalSurveyStates.heating_source)
    await message.answer("Выберите источник отопления.", reply_markup=options_keyboard(labels(HEATING_SOURCE_CHOICES)))


@router.message(LocalSurveyStates.heating_source)
async def local_heating_source_handler(message: Message, state: FSMContext):
    value = choice_map(HEATING_SOURCE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите источник отопления из списка.")
        return
    await state.update_data(heating_source=value)
    await state.set_state(LocalSurveyStates.personal_transport)
    await message.answer("Выберите личный транспорт.", reply_markup=options_keyboard(labels(PERSONAL_TRANSPORT_CHOICES)))


@router.message(LocalSurveyStates.personal_transport)
async def local_transport_handler(message: Message, state: FSMContext):
    value = choice_map(PERSONAL_TRANSPORT_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите вариант из списка.")
        return
    await state.update_data(personal_transport=value)
    if value == "none":
        await state.update_data(fuel_type="none", average_mileage_per_month=0)
        await state.set_state(LocalSurveyStates.public_transport)
        await message.answer(
            "Как часто вы пользуетесь общественным транспортом?",
            reply_markup=options_keyboard(labels(PUBLIC_TRANSPORT_USAGE_CHOICES)),
        )
        return
    await state.set_state(LocalSurveyStates.fuel_type)
    await message.answer("Выберите тип топлива.", reply_markup=options_keyboard(labels(FUEL_TYPE_CHOICES[1:])))


@router.message(LocalSurveyStates.fuel_type)
async def local_fuel_type_handler(message: Message, state: FSMContext):
    value = choice_map(FUEL_TYPE_CHOICES).get(message.text)
    if not value or value == "none":
        await message.answer("Выберите тип топлива из списка.")
        return
    await state.update_data(fuel_type=value)
    await state.set_state(LocalSurveyStates.mileage)
    await message.answer("Введите средний пробег в месяц, км.")


@router.message(LocalSurveyStates.mileage)
async def local_mileage_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 0:
        await message.answer("Введите корректный пробег.")
        return
    await state.update_data(average_mileage_per_month=int(message.text))
    await state.set_state(LocalSurveyStates.public_transport)
    await message.answer(
        "Как часто вы пользуетесь общественным транспортом?",
        reply_markup=options_keyboard(labels(PUBLIC_TRANSPORT_USAGE_CHOICES)),
    )


@router.message(LocalSurveyStates.public_transport)
async def local_public_transport_handler(message: Message, state: FSMContext):
    value = choice_map(PUBLIC_TRANSPORT_USAGE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите вариант из списка.")
        return
    await state.update_data(public_transport_usage=value)
    await state.set_state(LocalSurveyStates.flights_scope)
    await message.answer("Какие перелеты были за год?", reply_markup=options_keyboard(labels(FLIGHT_SCOPE_CHOICES)))


@router.message(LocalSurveyStates.flights_scope)
async def local_flights_scope_handler(message: Message, state: FSMContext):
    value = choice_map(FLIGHT_SCOPE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите вариант из списка.")
        return
    await state.update_data(flights_in_last_year=value)
    if value == "none":
        await state.update_data(flights_per_year=0, flight_type="economy")
        await state.set_state(LocalSurveyStates.waste)
        await message.answer("Как вы обращаетесь с отходами?", reply_markup=options_keyboard(labels(LOCAL_WASTE_CHOICES)))
        return
    await state.set_state(LocalSurveyStates.flights_per_year)
    await message.answer("Сколько перелетов было за год?")


@router.message(LocalSurveyStates.flights_per_year)
async def local_flights_per_year_handler(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Введите количество перелетов больше нуля.")
        return
    await state.update_data(flights_per_year=int(message.text))
    await state.set_state(LocalSurveyStates.flight_class)
    await message.answer("Выберите класс перелета.", reply_markup=options_keyboard(labels(FLIGHT_CLASS_CHOICES)))


@router.message(LocalSurveyStates.flight_class)
async def local_flight_class_handler(message: Message, state: FSMContext):
    value = choice_map(FLIGHT_CLASS_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите класс перелета из списка.")
        return
    await state.update_data(flight_type=value)
    await state.set_state(LocalSurveyStates.waste)
    await message.answer("Как вы обращаетесь с отходами?", reply_markup=options_keyboard(labels(LOCAL_WASTE_CHOICES)))


@router.message(LocalSurveyStates.waste)
async def local_waste_handler(message: Message, state: FSMContext):
    value = choice_map(LOCAL_WASTE_CHOICES).get(message.text)
    if not value:
        await message.answer("Выберите вариант из списка.")
        return
    raw_data = await state.get_data()
    answers = {
        "age": raw_data.get("age", 0),
        "housing_type": raw_data["housing_type"],
        "housing_area": raw_data["housing_area"],
        "people_in_home": raw_data["people_in_home"],
        "heating_source": raw_data["heating_source"],
        "personal_transport": raw_data["personal_transport"],
        "fuel_type": raw_data.get("fuel_type", "none"),
        "average_mileage_per_month": raw_data.get("average_mileage_per_month", 0),
        "public_transport_usage": raw_data["public_transport_usage"],
        "flights_in_last_year": raw_data["flights_in_last_year"],
        "flights_per_year": raw_data.get("flights_per_year", 0),
        "flight_type": raw_data.get("flight_type", "economy"),
        "waste_management": value,
    }
    result_text = save_and_render_result(message, "local", answers)
    await state.clear()
    await message.answer(result_text, reply_markup=ReplyKeyboardRemove())


def save_and_render_result(message: Message, user_type: str, answers: dict) -> str:
    survey_user = get_or_create_survey_user(
        source="telegram",
        user_type=user_type,
        external_id=str(message.from_user.id),
        age=answers.get("age"),
    )
    outcome = calculate_survey(user_type=user_type, answers=answers)
    recommendations, checklist = get_recommendations_for_outcome(outcome)
    result = persist_calculation_result(
        source="telegram",
        survey_user=survey_user,
        outcome=outcome,
        recommendations=recommendations,
        checklist=checklist,
        raw_identifier=str(message.from_user.id),
    )
    checklist_text = ""
    if checklist:
        checklist_text = f"\n\nЧек-лист:\n{checklist.content}"
        if checklist.url:
            checklist_text += f"\n{checklist.url}"
    return (
        f"Расчет завершен.\n"
        f"Итог: {result.total_emission:.2f} кг CO2e\n"
        f"Детализация: {result.breakdown}\n\n"
        f"Рекомендации:\n{result.recommendation_text}"
        f"{checklist_text}"
    )
