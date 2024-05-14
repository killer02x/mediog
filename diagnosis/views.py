from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateResponseMixin, View
from .forms import PreliminaryDiagnosisForm, RatingForm, UserRegisterForm, DoctorProfileForm, PatientProfileForm, DoctorRequestForm
from .models import DiagnosisHistory, Doctor, Rating, User, Patient
from .openai_integration import generate_text
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib import messages


from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

def role_redirect(request):
    user = request.user
    try:
        doctor = Doctor.objects.filter(user=user).first()
        if doctor and doctor.verified:
            # Если пользователь - верифицированный доктор
            return redirect('diagnosis:doctor_dashboard')
        elif Patient.objects.filter(user=user).exists():
            # Если пользователь - пациент
            return redirect('diagnosis:doctor_list')  # Предположим, что у вас есть отдельный дашборд для пациентов
        elif doctor and not doctor.verified:
            # Если пользователь - неверифицированный доктор
            return redirect('diagnosis:doctor_verifying')  # URL для страницы ожидания верификации доктора
        else:
            if user.is_doctor:
                return redirect('diagnosis:doctor_profile_create')
            elif user.is_patient:
                return redirect('diagnosis:patient_profile_create')
    except Exception as e:
        # В случае возникновения исключения, перенаправляем на страницу входа
        return redirect('login')

from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime
class PreliminaryDiagnosisFormView(FormView):
    template_name = 'diagnosis/form.html'
    form_class = PreliminaryDiagnosisForm

    def get_context_data(self, **kwargs):
        # Вызов базовой реализации, чтобы получить контекст
        context = super().get_context_data(**kwargs)
        # Получение doctor_pk из параметров запроса
        doctor_pk = self.kwargs.get('doctor_pk')
        context['doctor_pk'] = doctor_pk
        date_str = self.request.GET.get('date')
        slot_str = self.request.GET.get('slot').replace('.',
                                                        '').upper()  # Ensure that 'AM' or 'PM' is capitalized and without dots
        try:
            print(date_str, 'date_str.....')
            print(slot_str, 'slot_str.....')
            if 'AM' in slot_str or 'PM' in slot_str:
                print("---------")
                appointment_datetime = datetime.strptime(f'{date_str} {slot_str}', '%B %d, %Y %I %p')
                print('starwet.....')
            else:
                appointment_datetime = datetime.strptime(f'{date_str} {slot_str}', '%Y-%m-%d %H:%M')
            context['appointment_datetime'] = appointment_datetime
        except ValueError:
            # Handle the error if the date or time format is incorrect
            context['error'] = "The provided date and time format is incorrect."
        context['doctor'] = Doctor.objects.get(id=doctor_pk)

        return context

    def form_valid(self, form, **kwargs):
        # Формирование текста для запроса к API
        patient_data = form.cleaned_data
        text_to_send = f"""Пациент: {patient_data['full_name']}, {patient_data['age']} лет, {patient_data['gender']}.
        Контактная информация: {patient_data['phone']}.
        Текущие симптомы: {patient_data['symptoms']}, начавшиеся {patient_data['symptoms_start']}. Симптомы {patient_data['symptoms_frequency']}.
        Медицинская история: {patient_data['past_diseases_and_surgeries']}. Хронические заболевания: {patient_data['chronic_diseases']}. Семейная медицинская история: {patient_data['family_medical_history']}.
        Лекарства и добавки: {patient_data['medications']}. Витамины и добавки: {patient_data['supplements']}.
        Образ жизни: {patient_data['diet']}. Уровень физической активности: {patient_data['physical_activity_level']}. Вредные привычки: {patient_data['smoking_and_alcohol']}.
        Аллергии: {patient_data['allergies']}. Реакции на лекарства: {patient_data['drug_reactions']}.
        Общее самочувствие: {patient_data['appetite_and_weight_changes']}. Сон: {patient_data['sleep_changes']}. Стресс: {patient_data['stress_and_anxiety']}.
        На основе предоставленной информации, какие могут быть предварительные диагнозы? Какому врачу мне записаться?
        """

        # Получение ответа от ChatGPT API
        diagnoses = generate_text(text_to_send)
        doctor_pk = self.kwargs.get('doctor_pk')
        appointment_datetime_str = self.request.POST.get('appointment_datetime')
        appointment_datetime_str = appointment_datetime_str.replace('a.m.', 'AM').replace('p.m.', 'PM')
        date_format = "%Y-%m-%d %H:%M"
        try:
            appointment_datetime = datetime.strptime(appointment_datetime_str, date_format)
        except ValueError as e:
            print("There was an error converting the date:", e)
        print(appointment_datetime_str, '------------------------')
        doctor = get_object_or_404(Doctor, id=doctor_pk)
        appointment = Appointment.objects.create(patient=self.request.user.patient, doctor=doctor, date=appointment_datetime)
        DiagnosisHistory.objects.create(user=self.request.user.patient, text=diagnoses, patient_text=text_to_send, appointment=appointment)
        diagnosis_histories = DiagnosisHistory.objects.filter(user=self.request.user.patient)

        context = {
            'diagnoses': diagnoses,
            'diagnosis_histories': diagnosis_histories,
            'doctor_pk': doctor_pk,
            'doctor': doctor,
            'appointment': appointment
        }
        return render(self.request, template_name='diagnosis/form_result.html', context=context)

class PatientDiagnosisView(TemplateResponseMixin, View):
    template_name = 'diagnosis/form_result.html'

    def get(self, request):
        return self.render_to_response({})

class DoctorVarifingView(TemplateResponseMixin, View):
    template_name = 'doctors/waiting_varify.html'

    def get(self, request):
        return self.render_to_response({})
        


class DoctorListView(TemplateResponseMixin, View):
    template_name = 'doctors/list.html'

    def get(self, request):
        search_text = request.GET.get('search_text', '').strip()
        if search_text:
            # Создание запроса, нечувствительного к регистру, для поиска по ФИО, специальности и городу
            doctors = Doctor.objects.filter(
                Q(specialties__name__icontains=search_text) |
                Q(user__first_name__icontains=search_text) |
                Q(user__last_name__icontains=search_text) |
                Q(city__name__icontains=search_text)
            ).distinct()
        else:
            doctors = Doctor.objects.all()

        count = doctors.count()
        return self.render_to_response({'doctors': doctors, 'count': count, 'search_text': search_text})



from datetime import timedelta, time  # Импортируем time

def generate_time_slots(date, start_time, end_time, duration=30):
    """Генерирует список временных слотов на заданный день."""
    slots = []
    current_time = datetime.combine(date, start_time)
    end_time_combined = datetime.combine(date, end_time)
    while current_time + timedelta(minutes=duration) <= end_time_combined:
        slots.append(current_time.time())
        current_time += timedelta(minutes=duration)
    return slots

def generate_time_slots_for_week(start_date, start_time, end_time, duration=30):
    """Генерирует список временных слотов на неделю вперед."""
    slots = {}
    for day in range(7):  # Для каждого дня в неделе
        date = start_date + timedelta(days=day)
        slots[date] = generate_time_slots(date, start_time, end_time, duration)
    return slots

def get_available_slots(doctor_id, date, slots):
    """Возвращает доступные временные слоты для доктора."""
    appointments = Appointment.objects.filter(doctor_id=doctor_id, date__date=date)
    busy_slots = [appointment.date.time() for appointment in appointments]
    available_slots = [slot for slot in slots if slot not in busy_slots]
    return available_slots

class DoctorDetailView(TemplateResponseMixin, View):
    template_name = 'doctors/detail.html'

    def get(self, request, **kwargs):
        doctor_pk = self.kwargs.get('doctor_pk')
        doctor = get_object_or_404(Doctor, id=doctor_pk)
        ratings = Rating.objects.filter(doctor=doctor)
        form = RatingForm()

        # Получение сегодняшней даты, если дата начала не указана
        start_date_str = request.GET.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        # Генерация временных слотов на неделю
        slots_week = generate_time_slots_for_week(start_date, time(9, 0), time(17, 0), duration=60)
        available_slots_week = {}

        for date, slots in slots_week.items():
            available_slots = get_available_slots(doctor_pk, date, slots)
            available_slots_week[date] = available_slots

        return self.render_to_response({
            'doctor': doctor,
            'ratings': ratings,
            'form': form,
            'slots': available_slots_week
        })

    def post(self, request, **kwargs):
        doctor_pk = self.kwargs.get('doctor_pk')
        form = RatingForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.doctor = Doctor.objects.get(id=doctor_pk)
            form_obj.patient = request.user.patient
            form_obj.save()

        doctor = Doctor.objects.get(id=doctor_pk)
        ratings = Rating.objects.filter(doctor=doctor_pk)
        form = RatingForm(request.POST)
        return self.render_to_response({'doctor': doctor, 'ratings': ratings, 'form': form})

class DiagnosisHistoryView(TemplateResponseMixin, View):
    template_name = 'diagnosis/result_history.html'

    def get(self, request, **kwargs):
        diagnosis_histories = DiagnosisHistory.objects.filter(user=self.request.user.patient)
        return self.render_to_response({'diagnosis_histories': diagnosis_histories})

from django.shortcuts import redirect

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        self.user = form.save()  # Сохраняем пользователя
        role = form.cleaned_data.get('role')  # Получаем выбранную роль из формы
        if role == 'is_patient':
            self.user.is_patient = True
        elif role == 'is_doctor':
            self.user.is_doctor = True
        self.user.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Теперь self.user гарантированно существует
        print(self.user.is_doctor, '=========')
        if self.user.is_doctor:
            return reverse_lazy('diagnosis:doctor_profile_create')
        elif self.user.is_patient:
            return reverse_lazy('diagnosis:patient_profile_create')
        else:
            return reverse_lazy('login')


class DoctorProfileCreateView(LoginRequiredMixin, CreateView):
    model = Doctor
    form_class = DoctorProfileForm
    template_name = 'registration/doctor_profile_create.html'
    success_url = reverse_lazy('diagnosis:octor_varifing')  # Предполагается, что у вас есть URL с именем 'home'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PatientProfileCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientProfileForm
    template_name = 'registration/patient_profile_create.html'
    success_url = reverse_lazy('diagnosis:doctor_list')

    def form_valid(self, form):
        if Patient.objects.filter(user=self.request.user).exists():
            print(Patient.objects.filter(user=self.request.user), '++++++++++')
            messages.error(self.request, 'Профиль для данного пользователя уже существует.')
            return redirect('diagnosis:patient_profile_create')
        else:
            form.instance.user = self.request.user
            return super().form_valid(form)

from django.shortcuts import render
from django.views import View
from .models import Appointment, Patient
from .forms import PatientSearchForm


from django.shortcuts import render
from django.utils.timezone import now
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Appointment, Patient
from .forms import PatientSearchForm

class DoctorDashboardView(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        next_month = today + timedelta(days=30)
        
        total_patients_count = Patient.objects.count()  # Общее количество пациентов

        today_patients_count = Patient.objects \
    .annotate(appointment_count=Count('appointment', filter=Q(appointment__date__date=today))) \
    .filter(appointment_count__gt=0) \
    .count()
        
        
        today_appointments_count = Appointment.objects.filter(date__date=today).count()
        
        search_form = PatientSearchForm(request.GET)
        appointments = Appointment.objects.filter(doctor=request.user.doctor)

        if search_form.is_valid():
            identification_number = search_form.cleaned_data.get('identification_number')
            period = search_form.cleaned_data.get('period')

            if period == 'today':
                appointments = appointments.filter(date__date=today)
            elif period == 'next_week':
                appointments = appointments.filter(date__date__range=(today, next_week))
            elif period == 'next_month':
                appointments = appointments.filter(date__date__range=(today, next_month))

            if identification_number:
                appointments = appointments.filter(patient__identification_number=identification_number)

            appointments = appointments.order_by('date')  # Сортировка по дате

        return render(request, 'doctor_part/doctor_dashboard.html', {
            'total_patients_count': total_patients_count,
            'today_patients_count': today_patients_count,
            'today_appointments_count': today_appointments_count,
            'appointments': appointments,
            'search_form': search_form,
        })


from django.views.generic import DetailView

class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = 'doctor_part/patient_detail.html'
    context_object_name = 'appointment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.get_object()
        context['diagnosis_history'] = DiagnosisHistory.objects.get(appointment=appointment)
        return context

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def change_appointment_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor)
    if request.method == "POST":
        appointment.status = new_status
        appointment.save()
        # Перенаправление обратно на детальную страницу пациента
        return HttpResponseRedirect(reverse('diagnosis:patient_detail', args=[appointment.patient.id]))
    else:
        # Возвращаем пользователя обратно, если метод не POST
        return HttpResponseRedirect(reverse('diagnosis:patient_detail', args=[appointment.patient.id]))


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ChatMessage
from django.contrib.auth.decorators import login_required

@login_required
def chat_view(request, receiver_id):
    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver = User.objects.get(id=receiver_id)
        message = ChatMessage.objects.create(sender=request.user, receiver=receiver, text=message_text)
        return redirect('diagnosis:chat_view', receiver_id=receiver_id)
    else:
        receiver = User.objects.get(id=receiver_id)
        messages = ChatMessage.objects.filter(sender=request.user, receiver__id=receiver_id) | \
                   ChatMessage.objects.filter(sender__id=receiver_id, receiver=request.user)
        messages = messages.order_by('timestamp')
        return render(request, 'chat/chat.html', {'messages': messages, 'receiver_id': receiver_id, 'receiver': receiver})

@login_required
def fetch_messages(request, receiver_id):
    messages = ChatMessage.objects.filter(sender=request.user, receiver__id=receiver_id) | \
               ChatMessage.objects.filter(sender__id=receiver_id, receiver=request.user)
    messages = messages.order_by('timestamp')
    return JsonResponse({"messages": list(messages.values('sender__username', 'text', 'timestamp'))})

from .models import DoctorRequest, DonorRequest, DonorProfile
from django.http import HttpResponse

@login_required
def donor_registration_view(request):
    if request.method == 'POST':
        blood_type = request.POST.get('blood_type')
        age = request.POST.get('age')

        # Проверяем, есть ли у текущего пользователя профиль пациента
        try:
            patient = request.user.patient
        except Patient.DoesNotExist:
            return HttpResponse("Только пациенты могут регистрироваться в качестве доноров.", status=403)

        # Создаем профиль донора
        DonorProfile.objects.create(patient=patient, blood_type=blood_type, age=age)
        return redirect('diagnosis:donor_registration_confirm')

    # Если GET-запрос, отображаем пустую форму
    return render(request, 'donor/register.html')

@login_required
def donor_registration_confirm(request):
    return render(request, 'donor/confirm_register.html')

from .models import DoctorRequest
from django.db.models import Count


@login_required
def doctor_requests_list(request):
    requests = DoctorRequest.objects.annotate(response_count=Count('donorrequest'))

    # Инициализация переменных для избежания ошибок, если профиль донора отсутствует
    user_responses_ids = []
    user_responses = []

    # Попытка получить профиль донора текущего пользователя
    try:
        donor_profile = DonorProfile.objects.get(patient__user=request.user)
        # Получаем список ID заявок, на которые пользователь откликнулся
        user_responses_ids = DonorRequest.objects.filter(donor_profile=donor_profile).values_list('doctor_request_id', flat=True)
        # Получаем сами объекты откликов пользователя
        user_responses = DonorRequest.objects.filter(donor_profile=donor_profile).select_related('doctor_request')
    except DonorProfile.DoesNotExist:
        pass  # Если профиль донора не найден, списки остаются пустыми

    return render(request, 'donor/list.html', {
        'requests': requests,
        'user_responses_ids': list(user_responses_ids),
        'user_responses': user_responses,
    })


@login_required
def respond_to_doctor_request(request, request_id):
    doctor_request = get_object_or_404(DoctorRequest, id=request_id)
    donor_profile, created = DonorProfile.objects.get_or_create(patient=request.user.patient)

    # Проверяем, не откликался ли уже пользователь на эту заявку
    if not DonorRequest.objects.filter(donor_profile=donor_profile, doctor_request=doctor_request).exists():
        DonorRequest.objects.create(donor_profile=donor_profile, doctor_request=doctor_request)
        # Перенаправляем пользователя на страницу с подтверждением отклика или обратно к списку заявок
        return redirect('diagnosis:doctor_list')
    else:
        # Обработка случая, если пользователь уже откликался на заявку
        return redirect('diagnosis:doctor_list')


@login_required
def doctor_requests_list_doctor_part(request):
    all_requests = DoctorRequest.objects.annotate(response_count=Count('donorrequest'))

    # Проверяем, является ли текущий пользователь доктором
    try:
        current_doctor = request.user.doctor
        # Получаем заявки, созданные текущим доктором
        doctor_own_requests = DoctorRequest.objects.filter(doctor=current_doctor)
    except Doctor.DoesNotExist:
        doctor_own_requests = None

    return render(request, 'doctor_part/donor/list.html', {
        'all_requests': all_requests,
        'doctor_own_requests': doctor_own_requests,
    })


@login_required
def create_doctor_request(request):
    if not request.user.is_doctor:
        # Проверяем, что пользователь является доктором
        return redirect('diagnosis:doctor_requests_list')

    if request.method == 'POST':
        form = DoctorRequestForm(request.POST)
        if form.is_valid():
            doctor_request = form.save(commit=False)
            doctor_request.doctor = request.user.doctor
            doctor_request.save()
            return redirect('diagnosis:doctor_requests_list_doctor_part')  # Перенаправляем на список заявок
    else:
        form = DoctorRequestForm()
    return render(request, 'doctor_part/donor/create_doctor_request.html', {'form': form})

@login_required
def edit_doctor_request(request, request_id):
    doctor_request = get_object_or_404(DoctorRequest, id=request_id, doctor=request.user.doctor)
    if request.method == 'POST':
        form = DoctorRequestForm(request.POST, instance=doctor_request)
        if form.is_valid():
            form.save()
            return redirect('diagnosis:doctor_requests_list_doctor_part')  # Например, в список заявок
    else:
        form = DoctorRequestForm(instance=doctor_request)
    return render(request, 'doctor_part/donor/edit_doctor_request.html', {'form': form})

@login_required
def delete_doctor_request(request, request_id):
    doctor_request = get_object_or_404(DoctorRequest, id=request_id, doctor=request.user.doctor)
    doctor_request.delete()
    return redirect('diagnosis:doctor_requests_list_doctor_part')

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import DiscussionForm, CommentForm
from .models import Discussion, Comment

def discussion_list(request):
    discussions = Discussion.objects.all()
    return render(request, 'discussions/discussion_list.html', {'discussions': discussions})

from django.shortcuts import render, get_object_or_404, redirect
from .forms import CommentForm
from .models import Discussion, Comment

def discussion_detail(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    comments = Comment.objects.filter(discussion=discussion)  # Загрузка комментариев
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.user = request.user
            comment.save()
            return redirect('diagnosis:discussion_detail', pk=discussion.pk)
    else:
        form = CommentForm()
    return render(request, 'discussions/discussion_detail.html', {'discussion': discussion, 'comments': comments, 'form': form})


def create_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST, request.FILES)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.user = request.user
            discussion.save()
            return redirect('discussion_list.html', pk=discussion.pk)
    else:
        form = DiscussionForm()
    return render(request, 'discussions/create_discussion.html', {'form': form})
