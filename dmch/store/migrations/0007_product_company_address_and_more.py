# Generated by Django 5.0.3 on 2024-05-21 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_product_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='company_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productconsumption',
            name='company_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
