# Generated by Django 5.0.3 on 2024-06-07 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipd', '0007_patient_admission_dr_reg_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient_admission',
            name='dr_reg_no',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='patient_admission',
            name='regno',
            field=models.CharField(max_length=100),
        ),
    ]