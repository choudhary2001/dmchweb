# Generated by Django 5.0.3 on 2024-06-05 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counter', '0003_userlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlog',
            name='ip_address',
            field=models.CharField(blank=True, null=True),
        ),
    ]
