from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('secrets/', views.secrets, name='secrets'),
    path('surveys/', views.surveys, name='surveys'),
    path('gallery/', views.gallery, name='gallery'),
    path('survey/tourist/', views.tourist_survey, name='tourist_survey'),
    path('survey/local/', views.local_survey, name='local_survey'),
    path('survey/thank_you/', views.survey_thank_you, name='survey_thank_you'),
    path('survey/choice/', views.survey_choice, name='survey_choice')
]
