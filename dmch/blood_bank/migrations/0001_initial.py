# Generated by Django 5.0.3 on 2024-05-21 11:19

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
            name='BloodDonate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('donor_name', models.CharField(max_length=250)),
                ('father_name', models.CharField(max_length=250)),
                ('age', models.CharField(max_length=250)),
                ('gender', models.CharField(max_length=250)),
                ('address', models.TextField()),
                ('district', models.CharField(max_length=250)),
                ('mob_no', models.CharField(max_length=250)),
                ('vd', models.CharField(max_length=25)),
                ('vd_camp_name', models.CharField(max_length=250)),
                ('segment_no', models.CharField(max_length=250)),
                ('bag_no', models.CharField(max_length=250)),
                ('blood_group', models.CharField(max_length=25)),
                ('bag_type', models.CharField(max_length=25)),
                ('status', models.CharField(max_length=25)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BloodIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_name', models.CharField(max_length=250)),
                ('issue_bag_no', models.CharField(max_length=250)),
                ('blood_group', models.CharField(max_length=20)),
                ('blood_type', models.CharField(max_length=25)),
                ('org_type', models.CharField(max_length=25)),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('issue_type', models.CharField(max_length=50)),
                ('issue_number', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
