# Generated by Django 5.0.3 on 2024-05-16 20:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('counter', '0002_profile_data_add_profile_data_delete_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IpdDepartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_id', models.CharField(default='', editable=False, max_length=8, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('room_no', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='IpdDoctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_id', models.CharField(default='', editable=False, max_length=8, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ipd.ipddepartment')),
            ],
        ),
        migrations.CreateModel(
            name='Patient_Admission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_dmission_id', models.CharField(default='', editable=False, max_length=8, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('guardiannametitle', models.CharField(blank=True, max_length=100, null=True)),
                ('guardianname', models.CharField(max_length=255)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('days', models.IntegerField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=10, null=True)),
                ('mobno', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField()),
                ('district', models.CharField(max_length=100)),
                ('policest', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('pincode', models.CharField(blank=True, max_length=20, null=True)),
                ('disease', models.TextField()),
                ('death', models.BooleanField(default=False)),
                ('lama', models.BooleanField(default=False)),
                ('appointment_date', models.DateField(blank=True, null=True)),
                ('discharge_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ipd.ipddepartment')),
                ('patient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='counter.patient')),
                ('referby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ipd.ipddoctor')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
