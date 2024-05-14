from django.contrib import admin
from .models import User, Patient, Doctor, Specialty, PreliminaryDiagnosis, DiagnosisHistory, City, Appointment
from .models import DonorProfile, DoctorRequest, DonorRequest,Discussion,Comment


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'verified', 'phone_number')
    list_filter = ('verified', 'specialties')
    search_fields = ('user__username', 'phone_number', 'specialties__name')
    filter_horizontal = ('specialties',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone_number')
    search_fields = ('user__username', 'email', 'phone_number')

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'user', 'created_at')
    search_fields = ('discussion__title', 'user__username')
    list_filter = ('created_at',)

@admin.register(PreliminaryDiagnosis)
class PreliminaryDiagnosisAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender', 'phone')
    list_filter = ('gender', 'symptoms_start', 'symptoms_frequency', 'physical_activity_level', 'smoking_and_alcohol', 'appetite_and_weight_changes', 'sleep_changes', 'stress_and_anxiety')
    search_fields = ('full_name', 'symptoms', 'past_diseases_and_surgeries', 'chronic_diseases', 'family_medical_history', 'medications', 'supplements')

@admin.register(DiagnosisHistory)
class DiagnosisHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'text')

# Если вы еще не зарегистрировали модель User, вы можете сделать это также.
# Пример может выглядеть так, если вы хотите добавить дополнительную функциональность для пользователей:
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_patient', 'is_doctor')
    list_filter = ('is_patient', 'is_doctor')
    search_fields = ('username', 'email')


admin.site.register(City)
admin.site.register(Appointment)


class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('patient', 'blood_type', 'age', 'approved', 'created_at')
    list_filter = ('approved', 'blood_type')
    search_fields = ('patient__user__username', 'blood_type')

class DoctorRequestAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('doctor__user__username', 'title', 'description')

class DonorRequestAdmin(admin.ModelAdmin):
    list_display = ('donor_profile', 'doctor_request', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('donor_profile__patient__user__username', 'doctor_request__title')

admin.site.register(DonorProfile, DonorProfileAdmin)
admin.site.register(DoctorRequest, DoctorRequestAdmin)
admin.site.register(DonorRequest, DonorRequestAdmin)
