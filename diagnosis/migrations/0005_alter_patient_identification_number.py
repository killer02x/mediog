# Generated by Django 5.0.1 on 2024-02-29 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0004_patient_identification_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='identification_number',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]