# Generated by Django 5.0.1 on 2024-03-05 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0010_alter_diagnosishistory_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diagnosishistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='diagnosis.patient'),
        ),
    ]
