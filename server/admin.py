from django.contrib import admin
from .models import Student, Teacher, Course, Venue, Attendance, StudentRecord


# Register your models here.

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass
    


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    filter_horizontal = ('courses',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'lecturer')


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'radius')

@admin.register(StudentRecord)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student',)



@admin.register(Attendance )
class AttendanceAdmin(admin.ModelAdmin):
    filter_horizontal = ('present_students',)
    list_display = ('name', 'course', 'is_active', 'venue')

