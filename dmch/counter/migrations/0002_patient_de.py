# Generated by Django 5.0.3 on 2024-04-10 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='de',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
