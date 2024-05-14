from django import forms
from .models import PreliminaryDiagnosis, Rating, User, Doctor, Patient, Specialty
from django.contrib.auth.forms import UserCreationForm

class PreliminaryDiagnosisForm(forms.ModelForm):
    class Meta:
        model = PreliminaryDiagnosis
        fields = '__all__'  # Включает все поля модели

        # Опционально: добавление кастомных виджетов для отдельных полей
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'symptoms_start': forms.Select(attrs={'class': 'form-control'}),
            'symptoms_frequency': forms.Select(attrs={'class': 'form-control'}),
            'symptoms_relief_factors': forms.TextInput(attrs={'class': 'form-control'}),
            'past_diseases_and_surgeries': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'chronic_diseases': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'family_medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supplements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diet': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'physical_activity_level': forms.Select(attrs={'class': 'form-control'}),
            'smoking_and_alcohol': forms.Select(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'drug_reactions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'appetite_and_weight_changes': forms.Select(attrs={'class': 'form-control'}),
            'sleep_changes': forms.Select(attrs={'class': 'form-control'}),
            'stress_and_anxiety': forms.Select(attrs={'class': 'form-control'}),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'text']
        exclude = ('patient', 'doctor')


class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('is_patient', 'Patient'),
        ('is_doctor', 'Doctor'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'first_name', 'last_name']




class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['photo', 'about', 'license', 'diploma', 'specialization_certificates', 'liability_insurance', 'identification_document', 'phone_number', 'specialties']
        widgets = {'specialties': forms.CheckboxSelectMultiple}


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['email', 'phone_number', 'identification_number']


class PatientSearchForm(forms.Form):
    identification_number = forms.CharField(max_length=12, required=False, label='ИИН')
    period = forms.ChoiceField(choices=[('today', 'На сегодня'), ('next_week', 'На следующую неделю'), ('next_month', 'На следующий месяц')], required=False, label='Период')


from .models import DoctorRequest

class DoctorRequestForm(forms.ModelForm):
    class Meta:
        model = DoctorRequest
        fields = ['title', 'description']


from django import forms
from .models import Discussion, Comment

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content', 'photo']
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'photo']  # Добавляем поле 'photo'

