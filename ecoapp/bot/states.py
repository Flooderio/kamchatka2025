from aiogram.fsm.state import State, StatesGroup


class TouristSurveyStates(StatesGroup):
    route = State()
    departure_city = State()
    transfer = State()
    flight_class = State()
    days = State()
    accommodation = State()
    people_in_room = State()
    meal_type = State()
    meals_per_day = State()
    waste = State()
    local_transport = State()
    boat_duration = State()
    helicopter_duration = State()
    helicopter_passengers = State()


class LocalSurveyStates(StatesGroup):
    housing_type = State()
    housing_area = State()
    people_in_home = State()
    heating_source = State()
    personal_transport = State()
    fuel_type = State()
    mileage = State()
    public_transport = State()
    flights_scope = State()
    flights_per_year = State()
    flight_class = State()
    waste = State()
