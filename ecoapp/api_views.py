from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CalculationResult, City, Route, TransportType
from .serializers import (
    CalculationResultSerializer,
    CitySerializer,
    LocalSurveySerializer,
    RouteSerializer,
    TouristSurveySerializer,
    TransportTypeSerializer,
)
from .services.calculation import calculate_survey
from .services.persistence import get_or_create_survey_user, persist_calculation_result
from .services.recommendations import get_recommendations_for_outcome


class RouteListAPIView(generics.ListAPIView):
    queryset = Route.objects.filter(is_active=True).prefetch_related("transport_modes")
    serializer_class = RouteSerializer


class CityListAPIView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class TransportTypeListAPIView(generics.ListAPIView):
    queryset = TransportType.objects.filter(is_active=True)
    serializer_class = TransportTypeSerializer


class TouristCalculationAPIView(APIView):
    def post(self, request):
        serializer = TouristSurveySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(_save_api_result(request, "tourist", serializer.validated_data), status=status.HTTP_201_CREATED)


class LocalCalculationAPIView(APIView):
    def post(self, request):
        serializer = LocalSurveySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(_save_api_result(request, "local", serializer.validated_data), status=status.HTTP_201_CREATED)


class CalculationResultDetailAPIView(generics.RetrieveAPIView):
    queryset = CalculationResult.objects.all()
    serializer_class = CalculationResultSerializer


def _save_api_result(request, user_type: str, validated_data: dict) -> dict:
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    survey_user = get_or_create_survey_user(
        source="web",
        user_type=user_type,
        session_key=session_key,
        django_user=request.user,
        age=validated_data.get("age"),
    )
    outcome = calculate_survey(user_type=user_type, answers=validated_data)
    recommendations, checklist = get_recommendations_for_outcome(outcome)
    result = persist_calculation_result(
        source="web",
        survey_user=survey_user,
        outcome=outcome,
        recommendations=recommendations,
        checklist=checklist,
        raw_identifier=session_key or f"api-{survey_user.pk}",
    )
    return CalculationResultSerializer(result).data
