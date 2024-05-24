from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid
from counter.models import *
from radiology.models import *


class Cardiology(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null = True)
    cardiology_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    patient_name = models.CharField(max_length = 255, blank = True, null = True)
    patient = models.ForeignKey(Patient, on_delete = models.SET_NULL, blank = True, null = True)
    reg_no = models.CharField(max_length = 255, blank = True, null = True)
    gender = models.CharField(max_length = 255, blank = True, null = True)
    age = models.CharField(max_length = 255, blank = True, null = True)
    doctor = models.ForeignKey(RadiologyDoctor, on_delete = models.SET_NULL,  blank = True, null = True)
    department = models.ForeignKey(RadiologyDepartment, on_delete = models.SET_NULL,  blank = True, null = True)
    patient_type = models.CharField(max_length = 255, blank = True, null = True)
    add_time = models.DateTimeField(null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True, null = True, blank = True)
    def save(self, *args, **kwargs):
        if not self.cardiology_id:
            self.cardiology_id = str(uuid.uuid4().int)[:8]
        super(Cardiology, self).save(*args, **kwargs)

    def __str__(self):
        return self.patient_name

