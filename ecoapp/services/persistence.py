from __future__ import annotations

import hashlib

from ecoapp.models import CalculationResult, SurveyLocal, SurveyTourist, SurveyUser
from ecoapp.services.calculation import CalculationOutcome
from ecoapp.services.reporting import build_report_text


def get_or_create_survey_user(
    *,
    source: str,
    user_type: str,
    session_key: str | None = None,
    django_user=None,
    age: int | None = None,
    external_id: str | None = None,
) -> SurveyUser:
    if django_user and getattr(django_user, "is_authenticated", False):
        survey_user, _ = SurveyUser.objects.get_or_create(user=django_user)
    elif session_key:
        survey_user, _ = SurveyUser.objects.get_or_create(session_key=session_key)
    else:
        survey_user = SurveyUser.objects.create(session_key=external_id)

    survey_user.user_type = user_type
    survey_user.age = age
    if not survey_user.session_key and session_key:
        survey_user.session_key = session_key
    survey_user.save(update_fields=["user_type", "age", "session_key", "updated_at"])
    return survey_user


def build_anonymized_user_id(source: str, raw_identifier: str) -> str:
    return hashlib.sha256(f"{source}:{raw_identifier}".encode("utf-8")).hexdigest()


def persist_calculation_result(
    *,
    source: str,
    survey_user: SurveyUser | None,
    outcome: CalculationOutcome,
    recommendations,
    checklist,
    raw_identifier: str,
) -> CalculationResult:
    recommendation_codes = [item.code for item in recommendations]
    recommendation_text = "\n".join(f"{item.title}: {item.content}" for item in recommendations)
    report = build_report_text(outcome, recommendations, checklist)

    result = CalculationResult.objects.create(
        anonymized_user_id=build_anonymized_user_id(source, raw_identifier),
        source=source,
        user_type=outcome.user_type,
        route=outcome.route,
        factor_set=outcome.factor_set,
        checklist=checklist,
        answers=outcome.answers,
        breakdown=outcome.breakdown,
        total_emission=outcome.total_emission,
        recommendation_codes=recommendation_codes,
        recommendation_text=recommendation_text,
        report=report,
    )

    if survey_user:
        persist_legacy_surveys(survey_user=survey_user, outcome=outcome)
    return result


def persist_legacy_surveys(*, survey_user: SurveyUser, outcome: CalculationOutcome) -> None:
    answers = outcome.answers
    if outcome.user_type == "tourist":
        survey = SurveyTourist.objects.create(
            user=survey_user,
            route_id=answers.get("route"),
            departure_city_id=answers["departure_city"],
            is_transfer_in_moscow=answers["is_transfer_in_moscow"],
            flight_class=answers["flight_class"],
            days_in_location=answers["days_in_location"],
            accommodation_type=answers["accommodation_type"],
            people_in_room=answers["people_in_room"],
            meal_type=answers["meal_type"],
            meals_per_day=answers["meals_per_day"],
            waste_management=answers["waste_management"],
            boat_trip_duration=answers.get("boat_trip_duration") or "none",
            helicopter_ride_duration=answers.get("helicopter_ride_duration"),
            helicopter_ride_passengers=answers.get("helicopter_ride_passengers"),
        )
        if answers.get("local_transport_choices"):
            survey.transport_choices.set(answers["local_transport_choices"])
        if answers.get("tours"):
            survey.tours.set(answers["tours"])
        return

    SurveyLocal.objects.create(
        user=survey_user,
        housing_type=answers["housing_type"],
        people_in_home=answers["people_in_home"],
        housing_area=answers["housing_area"],
        heating_source=answers["heating_source"],
        personal_transport=answers["personal_transport"],
        fuel_type=answers["fuel_type"],
        average_mileage_per_month=answers["average_mileage_per_month"],
        public_transport_usage=answers["public_transport_usage"],
        flights_in_last_year=answers["flights_in_last_year"],
        flights_per_year=answers["flights_per_year"],
        flight_type=answers["flight_type"],
        waste_management=answers["waste_management"],
    )
