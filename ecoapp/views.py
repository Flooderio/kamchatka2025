from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms  import SurveyTouristForm, SurveyLocalForm 
from .models import SurveyUser, SurveyTourist, TransportOption, TransportType, Tour

def index(request):
    return render(request, 'ecoapp/index.html')

def base(request):
    return render(request, 'ecoapp/base.html')

def about(request):
    return render(request, 'ecoapp/about.html')

def secrets(request):
    return render(request, 'ecoapp/secrets.html')

def surveys(request):
    return render(request, 'ecoapp/surveys.html')

def gallery(request):
    return render(request, 'ecoapp/gallery.html')


def tourist_survey(request):
    user = request.user
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    survey_user, created = SurveyUser.objects.get_or_create(
        session_key=session_key,
        defaults={'user_id': request.user.id if request.user.is_authenticated else None}
    )
    if user.is_authenticated:
        survey_user, created = SurveyUser.objects.get_or_create(user=user)
    else:
        survey_user, created = SurveyUser.objects.get_or_create(session_key=session_key)

    if request.method == "POST":
        form = SurveyTouristForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.user = survey_user
            survey.save()
            return redirect('survey_thank_you')
        else:
            # Передаём туры даже при ошибке валидации
            tours = Tour.objects.prefetch_related('transport_choices').all()
            return render(request, 'ecoapp/tourist_survey.html', {'form': form, 'tours': tours})
    else:
        form = SurveyTouristForm()

    tours = Tour.objects.prefetch_related('transport_choices').all()

    return render(request, 'ecoapp/tourist_survey.html', {'form': form, 'tours': tours})


def survey_thank_you(request):
    return render(request, 'ecoapp/survey_thank_you.html')

def clean_people_in_room(self):
    people_in_room = self.cleaned_data.get('people_in_room')
    if people_in_room <= 0:
        raise ValidationError("Количество человек должно быть больше нуля.")
    return people_in_room

def local_survey(request):
    user = request.user
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    survey_user, created = SurveyUser.objects.get_or_create(
    session_key=session_key, defaults={'user_id': request.user.id if request.user.is_authenticated else None})
    
    if request.method == "POST":
        form = SurveyLocalForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.user = survey_user
            survey.save()
            return redirect('survey_thank_you')
        else:
            return render(request, 'ecoapp/survey_local.html', {'form': form})
    else:
        form = SurveyLocalForm()

    return render(request, 'ecoapp/survey_local.html', {'form': form})

def survey_choice(request):
    if request.method == 'POST':
        if 'local' in request.POST:
            return redirect('local_survey')
        elif 'tourist' in request.POST:
            return redirect('tourist_survey')
    return render(request, 'ecoapp/surveys.html')