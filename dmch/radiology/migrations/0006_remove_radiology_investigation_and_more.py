# Generated by Django 5.0.3 on 2024-05-15 21:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radiology', '0005_remove_radiology_investigation_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='radiology',
            name='investigation',
        ),
        migrations.AddField(
            model_name='radiology',
            name='investigation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='radiology.investigation'),
        ),
    ]
