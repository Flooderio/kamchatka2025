from django.urls import path

from .api_views import (
    CalculationResultDetailAPIView,
    CityListAPIView,
    LocalCalculationAPIView,
    RouteListAPIView,
    TouristCalculationAPIView,
    TransportTypeListAPIView,
)


urlpatterns = [
    path("routes/", RouteListAPIView.as_view(), name="api_routes"),
    path("cities/", CityListAPIView.as_view(), name="api_cities"),
    path("transport-types/", TransportTypeListAPIView.as_view(), name="api_transport_types"),
    path("calculate/tourist/", TouristCalculationAPIView.as_view(), name="api_calculate_tourist"),
    path("calculate/local/", LocalCalculationAPIView.as_view(), name="api_calculate_local"),
    path("results/<int:pk>/", CalculationResultDetailAPIView.as_view(), name="api_result_detail"),
]
