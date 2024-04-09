# Generated by Django 5.0.3 on 2024-04-09 09:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_id', models.CharField(default='', editable=False, max_length=8, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('room_no', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_id', models.CharField(default='', editable=False, max_length=8, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='counter.department')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('regno', models.CharField(max_length=100, unique=True)),
                ('regnoid', models.CharField(max_length=100)),
                ('regid', models.AutoField(primary_key=True, serialize=False)),
                ('uhidno', models.CharField(max_length=100)),
                ('uhidnoincre', models.CharField(max_length=100)),
                ('redcard', models.BooleanField(default=False)),
                ('redcardid', models.CharField(blank=True, max_length=255, null=True)),
                ('redcardtype', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('guardiannametitle', models.CharField(max_length=100)),
                ('guardianname', models.CharField(max_length=255)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('days', models.IntegerField(blank=True, null=True)),
                ('gender', models.CharField(max_length=10)),
                ('mobno', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('district', models.CharField(max_length=100)),
                ('policest', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('pincode', models.CharField(blank=True, max_length=20, null=True)),
                ('symptoms', models.TextField()),
                ('visittype', models.CharField(max_length=100)),
                ('appointment_date', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='counter.department')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='counter.doctor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_role', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
