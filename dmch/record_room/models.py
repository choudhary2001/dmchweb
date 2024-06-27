from django.db import models
from django.contrib.auth.models import User

class BHT(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    patient_id = models.CharField(max_length = 255, blank = True, null = True)
    patient_name = models.CharField(max_length = 255, blank = True, null = True)
    department = models.CharField(max_length = 255, blank = True, null = True)
    document = models.FileField(upload_to='bhtdocuments/')
    month = models.CharField(max_length = 50, blank = True, null = True)
    year = models.CharField(max_length = 50, blank = True, null = True)
    reason = models.CharField(max_length = 255, blank = True, null = True)
    icd = models.CharField(max_length = 255, blank = True, null = True)
    add_date = models.DateField(blank = True, null = True,)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.patient_name


class Injuiry(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    patient_id = models.CharField(max_length = 255, blank = True, null = True)
    patient_name = models.CharField(max_length = 255, blank = True, null = True)
    department = models.CharField(max_length = 255, blank = True, null = True)
    document = models.FileField(upload_to='injuirydocuments/')
    month = models.CharField(max_length = 50, blank = True, null = True)
    year = models.CharField(max_length = 50, blank = True, null = True)
    reason = models.CharField(max_length = 255, blank = True, null = True)
    icd = models.CharField(max_length = 255, blank = True, null = True)
    add_date = models.DateField(blank = True, null = True,)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.patient_name

class Death(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    patient_id = models.CharField(max_length = 255, blank = True, null = True)
    patient_name = models.CharField(max_length = 255, blank = True, null = True)
    department = models.CharField(max_length = 255, blank = True, null = True)
    document = models.FileField(upload_to='deathdocuments/')
    month = models.CharField(max_length = 50, blank = True, null = True)
    year = models.CharField(max_length = 50, blank = True, null = True)
    reason = models.CharField(max_length = 255, blank = True, null = True)
    icd = models.CharField(max_length = 255, blank = True, null = True)
    add_date = models.DateField(blank = True, null = True,)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.patient_name


