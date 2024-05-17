from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid
from counter.models import *

class IpdDepartment(models.Model):
    department_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length = 255)
    room_no = models.CharField(max_length = 255, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.department_id:
            self.department_id = str(uuid.uuid4().int)[:8]
        super(IpdDepartment, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class IpdDoctor(models.Model):
    doctor_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    department = models.ForeignKey(IpdDepartment, on_delete = models.SET_NULL, blank = True, null = True)
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = str(uuid.uuid4().int)[:8]
        super(IpdDoctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Patient_Admission(models.Model):
    patient_dmission_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null =True)
    department = models.ForeignKey(IpdDepartment, on_delete = models.SET_NULL,  blank = True, null = True)
    referby = models.ForeignKey(IpdDoctor, on_delete = models.SET_NULL, blank = True, null = True)
    patient = models.ForeignKey(Patient, on_delete = models.SET_NULL, blank = True, null =True)

    regno = models.CharField(max_length=100, unique = True)
    name = models.CharField(max_length=255,blank = True, null = True)
    guardiannametitle = models.CharField(max_length=100,blank = True, null = True)
    guardianname = models.CharField(max_length=255)
    year = models.IntegerField(blank = True, null = True)
    month = models.IntegerField(blank = True, null = True)
    days = models.IntegerField(blank = True, null = True)
    gender = models.CharField(max_length=10,blank = True, null = True)
    mobno = models.CharField(max_length=20,blank = True, null = True)
    address = models.TextField()
    district = models.CharField(max_length=100)
    policest = models.CharField(max_length=100, blank = True, null = True)
    state = models.CharField(max_length=100, blank = True, null = True)
    pincode = models.CharField(max_length=20, blank = True, null = True)

    disease = models.TextField()
    discharge = models.BooleanField(default=False)
    death = models.CharField(max_length=20, blank = True, null = True)
    lama = models.CharField(max_length=20, blank = True, null = True)

    appointment_date = models.DateTimeField(blank = True, null = True)
    discharge_date = models.DateTimeField(blank = True, null = True)
    
    created_at = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.patient_dmission_id:
            self.patient_dmission_id = str(uuid.uuid4().int)[:8]
        super(Patient_Admission, self).save(*args, **kwargs)
