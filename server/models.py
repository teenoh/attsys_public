import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from geoposition.fields import GeopositionField

import boto3
from raven.contrib.django.raven_compat.models import client

def delete_image(image_name):
    s3 = boto3.client('s3', region_name="us-east-2")
    try:
        s3.delete_object(Bucket='att-sys-media', Key=image_name)
    except:
        client.captureException()
    return

# Create your models here.
class Venue (models.Model):
    name = models.CharField(max_length=120)
    position = GeopositionField()
    radius = models.FloatField()
    #unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    @property
    def latitude(self):
        return self.position.latitude

    @property
    def longitude(self):
        return self.position.longitude

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def attendances(self):
        return 

    @property
    def courses(self):
        return self.course_set.all()
    
    @property
    def venues(self):
        return Venue.objects.all()

    def __str__(self):
        return "{}".format(self.user)

class Course(models.Model):
    name = models.CharField(blank=True, default="", max_length=100)
    code = models.CharField(blank=True, max_length=100)
    #unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    credits = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    lecturer = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    
    @property
    def lecturer_name(self):
        return self.lecturer.user.username

    def __str__(self):
        return "{}".format(self.code)
 
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mat_no = models.CharField(max_length=10, default="")
    picture = models.FileField(blank=True)
    courses = models.ManyToManyField(Course, related_name="students")

    @property
    def full_name(self):
        if self.user.first_name or self.user.last_name:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        return "{}".format(self.user.username)

    @property
    def ongoing_attendance(self):
        if self.courses.filter(attendances__is_active = True):
            return self.courses.filter(attendances__is_active = True)[0].attendances.filter(is_active=True)
        
        return []

    def __str__(self):
        return "{}".format(self.user.username)
 

class StudentRecord(models.Model):
    name = models.CharField(blank=True, max_length=120)
    student = models.ForeignKey(Student)
    picture = models.FileField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        return self.student.full_name

    @property
    def user(self):
        return self.student.user.username

    @property
    def mat_no(self):
        return self.student.mat_no

    @property
    def new_pic(self):
        return self.picture.url

    @property
    def reg_pic(self):
        return self.student.picture.url

    def delete(self, *args, **kwargs):
        if self.picture:
            delete_image(self.picture.name)
            
        super(StudentRecord, self).delete(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.student)


class Attendance(models.Model):
    name = models.CharField(default="", max_length=120)
    is_active = models.BooleanField(default=False)
    #unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendances")
    venue = models.ForeignKey(Venue)
    present_students = models.ManyToManyField(StudentRecord, blank=True)


    def __str__(self):
        return "{} - {}".format(self.course, self.name)

    