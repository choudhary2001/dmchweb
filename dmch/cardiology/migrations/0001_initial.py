# Generated by Django 5.0.3 on 2024-05-15 22:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('counter', '0001_initial'),
        ('radiology', '0008_remove_radiology_investigation_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cardiology',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cardiology_id', models.CharField(default='', editable=False, max_length=8, unique=True)),
                ('patient_name', models.CharField(blank=True, max_length=255, null=True)),
                ('reg_no', models.CharField(blank=True, max_length=255, null=True)),
                ('patient_type', models.CharField(blank=True, max_length=255, null=True)),
                ('add_time', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='radiology.radiologydepartment')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='radiology.radiologydoctor')),
                ('patient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='counter.patient')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
