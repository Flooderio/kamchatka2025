from django.shortcuts import get_object_or_404, redirect, render

from .forms import SurveyLocalForm, SurveyTouristForm
from .models import CalculationResult, Route, Tour
from .services.calculation import calculate_survey
from .services.persistence import get_or_create_survey_user, persist_calculation_result
from .services.recommendations import get_recommendations_for_outcome


def index(request):
    return render(request, "ecoapp/index.html")


def base(request):
    return render(request, "ecoapp/base.html")


def about(request):
    return render(request, "ecoapp/about.html")


def secrets(request):
    return render(request, "ecoapp/secrets.html")


def surveys(request):
    return render(request, "ecoapp/surveys.html")


def gallery(request):
    routes = Route.objects.filter(is_active=True).prefetch_related("transport_modes")
    return render(request, "ecoapp/gallery.html", {"routes": routes})


def tourist_survey(request):
    if request.method == "POST":
        form = SurveyTouristForm(request.POST)
        if form.is_valid():
            result = _handle_form_submission(
                request=request,
                user_type="tourist",
                cleaned_data=form.cleaned_data,
            )
            request.session["last_result_id"] = result.pk
            return redirect("survey_thank_you")
    else:
        form = SurveyTouristForm()

    tours = Tour.objects.prefetch_related("transport_choices").filter(is_active=True)
    return render(request, "ecoapp/tourist_survey.html", {"form": form, "tours": tours})


def local_survey(request):
    if request.method == "POST":
        form = SurveyLocalForm(request.POST)
        if form.is_valid():
            result = _handle_form_submission(
                request=request,
                user_type="local",
                cleaned_data=form.cleaned_data,
            )
            request.session["last_result_id"] = result.pk
            return redirect("survey_thank_you")
    else:
        form = SurveyLocalForm()

    return render(request, "ecoapp/survey_local.html", {"form": form})


def survey_thank_you(request):
    result_id = request.session.get("last_result_id")
    result = get_object_or_404(CalculationResult, pk=result_id) if result_id else None
    return render(request, "ecoapp/survey_thank_you.html", {"result": result})


def survey_choice(request):
    if request.method == "POST":
        if "local" in request.POST:
            return redirect("local_survey")
        if "tourist" in request.POST:
            return redirect("tourist_survey")
    return render(request, "ecoapp/surveys.html")


def _handle_form_submission(*, request, user_type: str, cleaned_data: dict) -> CalculationResult:
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    survey_user = get_or_create_survey_user(
        source="web",
        user_type=user_type,
        session_key=session_key,
        django_user=request.user,
        age=cleaned_data.get("age"),
    )
    outcome = calculate_survey(user_type=user_type, answers=cleaned_data)
    recommendations, checklist = get_recommendations_for_outcome(outcome)
    return persist_calculation_result(
        source="web",
        survey_user=survey_user,
        outcome=outcome,
        recommendations=recommendations,
        checklist=checklist,
        raw_identifier=session_key or f"web-{survey_user.pk}",
    )