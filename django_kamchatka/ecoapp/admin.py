from django.contrib import admin
from .models import SurveyUser, SurveyTourist, SurveyLocal, TransportActivity, TransportType, TransportOption

class TransportOptionInline(admin.TabularInline):
    model = TransportOption
    extra = 1

class SurveyTouristAdmin(admin.ModelAdmin):
    inlines = [TransportOptionInline]

admin.site.register(SurveyUser)
admin.site.register(SurveyTourist, SurveyTouristAdmin)
admin.site.register(SurveyLocal)
admin.site.register(TransportActivity)
admin.site.register(TransportType)
