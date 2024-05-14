# Generated by Django 5.0.1 on 2024-02-12 09:11

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PreliminaryDiagnosis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский'), ('other', 'Другое')], max_length=6)),
                ('phone', models.CharField(max_length=20)),
                ('symptoms', models.TextField()),
                ('symptoms_start', models.CharField(choices=[('less_week', 'Менее недели назад'), ('one_two_weeks', '1-2 недели назад'), ('more_month', 'Более месяца назад')], max_length=15)),
                ('symptoms_frequency', models.CharField(choices=[('daily', 'Ежедневно'), ('several_week', 'Несколько раз в неделю'), ('rarely', 'Редко')], max_length=15)),
                ('past_diseases_and_surgeries', models.TextField(blank=True)),
                ('chronic_diseases', models.TextField(blank=True)),
                ('family_medical_history', models.TextField(blank=True)),
                ('medications', models.TextField(blank=True)),
                ('supplements', models.TextField(blank=True)),
                ('diet', models.TextField(blank=True)),
                ('physical_activity_level', models.CharField(blank=True, choices=[('low', 'Низкий'), ('moderate', 'Умеренный'), ('high', 'Высокий')], max_length=10)),
                ('smoking_and_alcohol', models.CharField(blank=True, choices=[('none', 'Нет'), ('smoking', 'Курение'), ('alcohol', 'Алкоголь'), ('both', 'И то, и другое')], max_length=10)),
                ('allergies', models.TextField(blank=True)),
                ('drug_reactions', models.TextField(blank=True)),
                ('appetite_and_weight_changes', models.CharField(blank=True, choices=[('no_change', 'Без изменений'), ('increase', 'Увеличение'), ('decrease', 'Уменьшение')], max_length=10)),
                ('sleep_changes', models.CharField(blank=True, choices=[('normal', 'Нормальный'), ('insomnia', 'Бессонница'), ('disturbed', 'Нарушенный')], max_length=10)),
                ('stress_and_anxiety', models.CharField(blank=True, choices=[('none', 'Нет'), ('occasional', 'Иногда'), ('frequent', 'Часто')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Specialty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_patient', models.BooleanField(default=False)),
                ('is_doctor', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.FileField(blank=True, null=True, upload_to='licenses/')),
                ('about', models.TextField()),
                ('license', models.FileField(blank=True, null=True, upload_to='licenses/')),
                ('diploma', models.FileField(blank=True, null=True, upload_to='diplomas/')),
                ('specialization_certificates', models.FileField(blank=True, null=True, upload_to='specializations/')),
                ('liability_insurance', models.FileField(blank=True, null=True, upload_to='insurance/')),
                ('identification_document', models.FileField(blank=True, null=True, upload_to='identifications/')),
                ('phone_number', models.CharField(max_length=15)),
                ('verified', models.BooleanField(default=False)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doctors', to='diagnosis.city')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('specialties', models.ManyToManyField(related_name='doctors', to='diagnosis.specialty')),
            ],
        ),
        migrations.CreateModel(
            name='DiagnosisHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diagnosis.doctor')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=15)),
                ('phone_number', models.CharField(max_length=15)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('text', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diagnosis.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diagnosis.patient')),
            ],
        ),
    ]
