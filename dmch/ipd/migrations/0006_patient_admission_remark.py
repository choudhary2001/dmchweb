# Generated by Django 5.0.3 on 2024-05-20 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipd', '0005_alter_patient_admission_death_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient_admission',
            name='remark',
            field=models.CharField(blank=True, max_length=355, null=True),
        ),
    ]