# Generated by Django 5.0.3 on 2024-05-17 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine_store', '0003_medicine_departpment_medicineconsumption_departpment'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicineconsumption',
            name='patient_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='medicineconsumption',
            name='regno',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]