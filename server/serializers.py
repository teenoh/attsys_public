from rest_framework import serializers

from .models import Student, Course, Attendance, Venue, Teacher, StudentRecord



class CourseSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = Course
        fields = ('id', 'name', 'code', 'credits', 'description', 'lecturer_name')

class VenueSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = Venue
        fields = ('id', 'name', 'latitude', 'longitude', 'radius')


class AttendanceSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    venue = VenueSerializer()

    class Meta():
        model = Attendance
        fields = ('id', 'name','course', 'venue')



class StudentSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)
    ongoing_attendance = AttendanceSerializer(many=True)

    class Meta():
        model = Student
        fields = ('user', 'picture', 'mat_no', 'courses', 'ongoing_attendance')



########################Teacher section start

class StudentRecordSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = StudentRecord
        fields = ('user', 'mat_no', 'full_name', 'reg_pic', 'picture', 'timestamp')

class VenueProSerializer(serializers.ModelSerializer):
    
    class Meta():
        model = Venue
        fields = ('name',)


class AttendanceProSerializer(serializers.ModelSerializer):
    venue = serializers.CharField()
    present_students = StudentRecordSerializer(many=True)
        
    class Meta():
        model = Attendance
        fields = ('id', 'name', 'venue', 'is_active', 'present_students')


class CourseProSerializer(serializers.ModelSerializer):
    attendances = AttendanceProSerializer(many=True)

    class Meta():
        model = Course
        fields = ('id','name','code', 'credits', 'description', 'attendances')




class TeacherSerializer(serializers.ModelSerializer):
    courses = CourseProSerializer(many=True)
    venues = VenueSerializer(many=True)

    class Meta():
        model = Teacher
        fields = ("user", "courses", "venues")


#######################Teacher section end

class VerifySerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        return validated_data
        # return People.objects.create(**validated_data)


    # def validate(self, data, *args, **kwargs):
    #     """
    #         Check that user is a student
    #     """
    #     if Student.objects.get(user = data['user']):
    #         return data
    #     raise serializers.ValidationError("User must be a registered student")