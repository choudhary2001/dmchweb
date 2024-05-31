# Generated by Django 5.0.3 on 2024-05-31 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record_room', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Death',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.CharField(blank=True, max_length=255, null=True)),
                ('patient_name', models.CharField(blank=True, max_length=255, null=True)),
                ('department', models.CharField(blank=True, max_length=255, null=True)),
                ('document', models.FileField(upload_to='deathdocuments/')),
                ('month', models.CharField(blank=True, max_length=50, null=True)),
                ('year', models.CharField(blank=True, max_length=50, null=True)),
                ('reason', models.CharField(blank=True, max_length=255, null=True)),
                ('icd', models.CharField(blank=True, max_length=255, null=True)),
                ('add_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Injuiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.CharField(blank=True, max_length=255, null=True)),
                ('patient_name', models.CharField(blank=True, max_length=255, null=True)),
                ('department', models.CharField(blank=True, max_length=255, null=True)),
                ('document', models.FileField(upload_to='injuirydocuments/')),
                ('month', models.CharField(blank=True, max_length=50, null=True)),
                ('year', models.CharField(blank=True, max_length=50, null=True)),
                ('reason', models.CharField(blank=True, max_length=255, null=True)),
                ('icd', models.CharField(blank=True, max_length=255, null=True)),
                ('add_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]