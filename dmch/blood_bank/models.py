from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid

class BloodIssue(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null =True)
    patient_name = models.CharField(max_length = 250)
    father_name = models.CharField(max_length = 250, blank = True, null = True)
    age = models.CharField(max_length = 250, blank = True, null = True)
    gender = models.CharField(max_length = 250, blank = True, null = True)
    address = models.TextField()
    district = models.CharField(max_length = 250, blank = True, null = True)
    mob_no = models.CharField(max_length = 250, blank = True, null = True)
    issue_bag_no = models.CharField(max_length = 250, blank = True, null = True)
    blood_group = models.CharField(max_length = 20, blank = True, null = True)
    blood_type = models.CharField(max_length = 25, blank = True, null = True)
    org_type = models.CharField(max_length = 25, blank = True, null = True)
    org_name = models.CharField(max_length = 25, blank = True, null = True)
    issue_type = models.CharField(max_length = 50, blank = True, null = True)
    issue_number = models.CharField(max_length = 50, blank = True, null = True)
    issue_date = models.DateField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.patient_name


class BloodDonate(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null =True)
    donor_name = models.CharField(max_length = 250)
    father_name = models.CharField(max_length = 250)
    age = models.CharField(max_length = 250)
    gender = models.CharField(max_length = 250)
    address = models.TextField()
    district = models.CharField(max_length = 250)
    mob_no = models.CharField(max_length = 250)
    vd = models.CharField(max_length = 25)
    vd_camp_name = models.CharField(max_length = 250)
    segment_no = models.CharField(max_length = 250)
    bag_no = models.CharField(max_length = 250)
    blood_group = models.CharField(max_length = 25)
    bag_type = models.CharField(max_length = 25)
    status = models.CharField(max_length = 25)
    add_date = models.DateTimeField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return self.donor_name


class BloodStock(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null =True)
    blooddonate = models.ForeignKey(BloodDonate, on_delete = models.CASCADE, blank = True, null =True)
    segment_no = models.CharField(max_length = 250)
    bag_no = models.CharField(max_length = 250)
    blood_group = models.CharField(max_length = 25)
    bag_type = models.CharField(max_length = 25)
    blood_type = models.CharField(max_length = 25, blank = True, null = True)
    status = models.CharField(max_length = 25)
    add_date = models.DateTimeField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.segment_no
