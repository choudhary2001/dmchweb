# Generated by Django 5.0.3 on 2024-05-20 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_product_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='company_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
