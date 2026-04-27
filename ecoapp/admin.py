from django.contrib import admin

from .models import (
    CalculationResult,
    Checklist,
    City,
    EmissionFactor,
    FactorSet,
    Recommendation,
    Route,
    SurveyLocal,
    SurveyTourist,
    SurveyUser,
    Tour,
    TransportActivity,
    TransportOption,
    TransportType,
)


class TransportOptionInline(admin.TabularInline):
    model = TransportOption
    extra = 0


@admin.register(SurveyTourist)
class SurveyTouristAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "route", "departure_city", "created_at")
    list_filter = ("route", "flight_class", "accommodation_type", "created_at")
    search_fields = ("user__session_key", "departure_city__name")
    inlines = [TransportOptionInline]
    filter_horizontal = ("transport_choices", "tours")


@admin.register(SurveyLocal)
class SurveyLocalAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "housing_type", "personal_transport", "created_at")
    list_filter = ("housing_type", "heating_source", "personal_transport", "created_at")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "default_duration_days", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    filter_horizontal = ("transport_modes",)


@admin.register(FactorSet)
class FactorSetAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "is_active", "is_draft", "created_at")
    list_filter = ("is_active", "is_draft")
    search_fields = ("name", "code", "version")


@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ("factor_set", "category", "subtype", "value", "unit", "is_temporary")
    list_filter = ("factor_set", "category", "is_temporary")
    search_fields = ("category", "subtype", "name")


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "user_type", "trigger_category", "min_total_emission", "is_active")
    list_filter = ("user_type", "trigger_category", "is_active")


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "user_type", "is_active")
    list_filter = ("user_type", "is_active")


@admin.register(CalculationResult)
class CalculationResultAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "user_type", "route", "total_emission", "created_at")
    list_filter = ("source", "user_type", "created_at")
    search_fields = ("anonymized_user_id",)
    readonly_fields = ("answers", "breakdown", "recommendation_codes", "report")


admin.site.register(SurveyUser)
admin.site.register(TransportActivity)
admin.site.register(TransportType)
admin.site.register(Tour)
admin.site.register(City)
