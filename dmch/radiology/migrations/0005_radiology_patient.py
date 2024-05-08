# Generated by Django 5.0.3 on 2024-05-08 19:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counter', '0001_initial'),
        ('radiology', '0004_investigation_investigation_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='radiology',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='counter.patient'),
        ),
    ]
