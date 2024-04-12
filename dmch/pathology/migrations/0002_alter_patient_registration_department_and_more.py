# Generated by Django 5.0.3 on 2024-04-11 09:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pathology', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient_registration',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pathology.pathologydepartment'),
        ),
        migrations.AlterField(
            model_name='patient_registration',
            name='referby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pathology.pathologydoctor'),
        ),
    ]
