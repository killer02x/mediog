# Generated by Django 5.0.1 on 2024-02-29 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0003_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='identification_number',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True),
        ),
    ]