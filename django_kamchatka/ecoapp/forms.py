from django import forms
from .models import SurveyTourist, TransportType, TransportOption, SurveyLocal, Tour

class SurveyTouristForm(forms.ModelForm):
    tours = forms.ModelMultipleChoiceField(
        queryset=Tour.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите экскурсии"
    )

    class Meta:
        model = SurveyTourist
        fields = [
            "departure_city", "is_transfer_in_moscow", "flight_class",
            "days_in_location", "accommodation_type", "people_in_room",
            "meal_type", "meals_per_day", "waste_management", "tours",
            "boat_trip_duration", "helicopter_ride_duration", "helicopter_ride_passengers"
        ]
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if not (18 <= age <= 150):
            raise forms.ValidationError("Возраст должен быть от 18 до 150 лет.")
        return age

    def clean_people_in_room(self):
        people_in_room = self.cleaned_data.get('people_in_room')
        if people_in_room <= 0:
            raise forms.ValidationError("Количество человек должно быть больше нуля.")
        return people_in_room

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'tours' in self.data:
            selected_tours = self.data.getlist('tours')
            if selected_tours:
                tours = Tour.objects.filter(id__in=selected_tours)
                transport_options = TransportOption.objects.filter(tour__in=tours)
                transport_types = TransportType.objects.filter(id__in=transport_options.values('transport_id'))
                self.fields['transport_choices'].queryset = transport_types


class SurveyLocalForm(forms.ModelForm):
    class Meta:
        model = SurveyLocal
        fields = ['housing_type', 'people_in_home', 'housing_area', 'heating_source', 'personal_transport', 
                  'fuel_type', 'average_mileage_per_month', 'public_transport_usage', 'flights_in_last_year', 
                  'flight_type', 'waste_management']

