from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=15)
    identification_number = models.CharField(max_length=15, unique=True, null=True, blank=True)


# Модель для специализаций
class Specialty(models.Model):
    name = models.CharField(max_length=100)  # Название специализации, например, хирург, невролог и т.д.
    description = models.TextField(null=True, blank=True)  # Описание специализации

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialties = models.ManyToManyField(Specialty, related_name='doctors')  # Специализации врача
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='doctors')
    photo = models.FileField(upload_to='licenses/', null=True, blank=True)
    about = models.TextField()
    license = models.FileField(upload_to='licenses/', null=True, blank=True)  # Лицензия на медицинскую практику
    diploma = models.FileField(upload_to='diplomas/', null=True, blank=True)  # Диплом о высшем образовании
    specialization_certificates = models.FileField(upload_to='specializations/', null=True, blank=True)  # Сертификаты специализации
    liability_insurance = models.FileField(upload_to='insurance/', null=True, blank=True)  # Страхование профессиональной ответственности
    identification_document = models.FileField(upload_to='identifications/', null=True, blank=True)  # Идентификационные документы
    phone_number = models.CharField(max_length=15)
    verified = models.BooleanField(default=False)  # Поле для верификации доктора администратором
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.user.username

from mediog import settings


class PreliminaryDiagnosis(models.Model):
    # Основная информация
    full_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender_choices = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('other', 'Другое')
    ]
    gender = models.CharField(max_length=6, choices=gender_choices)

    # Контактная информация
    phone = models.CharField(max_length=20)

    # Текущие Симптомы
    symptoms = models.TextField()
    symptoms_start_choices = [
        ('less_week', 'Менее недели назад'),
        ('one_two_weeks', '1-2 недели назад'),
        ('more_month', 'Более месяца назад')
    ]
    symptoms_start = models.CharField(max_length=15, choices=symptoms_start_choices)
    symptoms_frequency_choices = [
        ('daily', 'Ежедневно'),
        ('several_week', 'Несколько раз в неделю'),
        ('rarely', 'Редко')
    ]
    symptoms_frequency = models.CharField(max_length=15, choices=symptoms_frequency_choices)

    # Медицинская история
    past_diseases_and_surgeries = models.TextField(blank=True)
    chronic_diseases = models.TextField(blank=True)
    family_medical_history = models.TextField(blank=True)

    # Лекарства и добавки
    medications = models.TextField(blank=True)
    supplements = models.TextField(blank=True)

    # Образ жизни
    diet = models.TextField(blank=True)
    physical_activity_level_choices = [
        ('low', 'Низкий'),
        ('moderate', 'Умеренный'),
        ('high', 'Высокий')
    ]
    physical_activity_level = models.CharField(max_length=10, choices=physical_activity_level_choices, blank=True)
    smoking_and_alcohol_choices = [
        ('none', 'Нет'),
        ('smoking', 'Курение'),
        ('alcohol', 'Алкоголь'),
        ('both', 'И то, и другое')
    ]
    smoking_and_alcohol = models.CharField(max_length=10, choices=smoking_and_alcohol_choices, blank=True)

    # Аллергии и реакции
    allergies = models.TextField(blank=True)
    drug_reactions = models.TextField(blank=True)

    # Общее самочувствие
    appetite_and_weight_changes_choices = [
        ('no_change', 'Без изменений'),
        ('increase', 'Увеличение'),
        ('decrease', 'Уменьшение')
    ]
    appetite_and_weight_changes = models.CharField(max_length=10, choices=appetite_and_weight_changes_choices, blank=True)
    sleep_changes_choices = [
        ('normal', 'Нормальный'),
        ('insomnia', 'Бессонница'),
        ('disturbed', 'Нарушенный')
    ]
    sleep_changes = models.CharField(max_length=10, choices=sleep_changes_choices, blank=True)
    stress_and_anxiety_choices = [
        ('none', 'Нет'),
        ('occasional', 'Иногда'),
        ('frequent', 'Часто')
    ]
    stress_and_anxiety = models.CharField(max_length=10, choices=stress_and_anxiety_choices, blank=True)

    def __str__(self):
        return self.full_name

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')

    def __str__(self):
        return f"{self.patient} - {self.doctor} on {self.date.strftime('%Y-%m-%d %H:%M')}"

class DiagnosisHistory(models.Model):
    user = models.ForeignKey(Patient, on_delete=models.CASCADE)
    text = models.TextField()
    patient_text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)


class Rating(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    rating = models.IntegerField()
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class DonorProfile(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3)
    age = models.PositiveIntegerField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donor profile of {self.patient.user.username}"


class DoctorRequest(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.doctor.user.username} - {self.title}"


class DonorRequest(models.Model):
    donor_profile = models.ForeignKey(DonorProfile, on_delete=models.CASCADE)
    doctor_request = models.ForeignKey(DoctorRequest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


from django.db import models
from django.conf import settings

class Discussion(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    photo = models.ImageField(upload_to='discussion_photos/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
from django.db import models
from django.conf import settings

class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    photo = models.ImageField(upload_to='comment_photos/', blank=True, null=True)  # Поле для фото
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.discussion}"






