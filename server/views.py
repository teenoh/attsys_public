import uuid
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import  IsAuthenticated


from .serializers import VerifySerializer, StudentSerializer, TeacherSerializer
from .rekog import recognize
from .models import Student, Teacher, Course, Venue, StudentRecord
from .models import Venue as VenueModel
from .models import Attendance as AttendanceModel
from .permissions import PostOwnStatus
import boto3
import logging

from raven.contrib.django.raven_compat.models import client

def delete_image(image_name):
    s3 = boto3.client('s3', region_name="us-east-2")
    try:
        s3.delete_object(Bucket='att-sys-media', Key=image_name)
    except:
        client.captureException()

def upload_images(image, user):
    s3 = boto3.client('s3', region_name="us-east-2")
    filename = '{}_test.jpg'.format(user)
    bucket_name = 'att-sys-media'
    try:
        logging.info("before image upload")
        status = s3.upload_fileobj(image, bucket_name, filename)
        logging.info("after image upload")
        return True
    except:
        client.captureException()
        return False
   
class LoginViewSet(viewsets.ViewSet):
    """Checks email and password and returns auth token"""

    serializer_class = AuthTokenSerializer

    def create(self, request):
        """Use the ObtainAuthToken APIView to validate and create a token""" 

        return ObtainAuthToken().post(request)

class StudentViewSet(viewsets.ModelViewSet):
    """
        return student data
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        print(request.user)
        
        if not Student.objects.get(user__username = request.user):
            return Response({"errors": ["student not registered"]}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Student.objects.get(user__username = request.user)
        serializer = StudentSerializer(queryset)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """sets user profile to the logged in user"""

        serializer.save(user=self.request.user)

class TeacherViewSet(viewsets.ModelViewSet):
    """
        return teacher data
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = TeacherSerializer
    queryset = Teacher.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        queryset = Teacher.objects.get(user__username = request.user)
        serializer = TeacherSerializer(queryset)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """sets user profile to the logged in user"""

        serializer.save(user=self.request.user)


class CoursesDetails(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs ):
        if Student.objects.get(user = request.user):
            student = Student.objects.get(user = request.user)

            return Response({"errors": ["student not registered"]}, status=status.HTTP_400_BAD_REQUEST)    


class VerifyPicture(APIView):
    parser_classes = (MultiPartParser, FormParser)
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        #get student object
        if Student.objects.get(user = request.user):
            student = Student.objects.get(user = request.user)

            #check if attendance pk was sent
            if not request.data.get('pk', ''):
                return Response({"errors": ["Attendance primary key not sent"]}, status=status.HTTP_400_BAD_REQUEST) 

            pk = request.data['pk']

            #check if file was sent
            if request.FILES.get('file', ''):
                '''Checking if image match'''

                print(dir(request.FILES['file']))
                
                #check if fake primary key was sent
                if not AttendanceModel.objects.get(id=pk):
                    return Response({"errors": ["Fake Primary key sent"]}, status=status.HTTP_400_BAD_REQUEST)
                

                attendance = AttendanceModel.objects.get(id=pk)

                #check if attendance is ongoing
                if (attendance.is_active == False):
                    return Response({"errors": ["Attendance taking has ended"]}, status=status.HTTP_400_BAD_REQUEST)
                
                #get or create a new StudentRecord Object
                try:
                    student_record, created = StudentRecord.objects.get_or_create(student=student, name="{}_{}_".format(student.user, attendance.pk))
                    print(student_record)
                    print("created  =>  ", created)
                except:
                    return Response({"errors": ["An error occured. Try again"]}, status=status.HTTP_400_BAD_REQUEST)                    

                #check student has already been signed in
                if (student_record in attendance.present_students.all()):
                    return Response({"errors": ["Your attendance has already been taken"]}, status=status.HTTP_400_BAD_REQUEST)

                #update student_record picture
                try:
                    new_pic = request.FILES['file'] 
                    new_pic.name = "{}_{}_.jpg".format(student.user.username, attendance.pk)
                    print(new_pic.name)
                    student_record.picture = new_pic

                except:
                    student_record.delete()
                    return Response({"errors": ["Error occured in uploading the picture"]}, status=status.HTTP_400_BAD_REQUEST)

                #save student record instance

                student_record.save()

                #facial recognition
                try:
                    result = recognize(str(student.picture), str(student_record.picture)) 
                except:
                    client.captureException()
                
                if (result > 80):
                    attendance.present_students.add(student_record)
                    attendance.save()
                    return Response({'message': 'You have been marked present' ,'similarity': "{}%".format(result)}, status=status.HTTP_200_OK)

                
                #once facial recognition fails, delete la pic
                #delete_image(student_record.picture.name)
                student_record.delete()

                return Response({"errors": ["Facial recognition test failed"], 'similarity': "{}%".format(result)}, status=status.HTTP_400_BAD_REQUEST)                    

            return Response({"errors": ["Picture was not sent"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"errors": ["student not registered"]}, status=status.HTTP_400_BAD_REQUEST)          

# class VerifyPicture(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
    
#     def post(self, request, *args, **kwargs):
        
#         if Student.objects.get(user = request.user):
#             student = Student.objects.get(user = request.user)

#             if not request.data.get('pk', ''):
#                 return Response({"errors": ["Attendance primary key not sent"]}, status=status.HTTP_400_BAD_REQUEST) 

#             pk = request.data['pk']

#             if request.FILES.get('file', ''):
#                 '''Checking if image match'''

#                 upload_result = upload_images(request.FILES['file'], student.user.username) 

#                 if upload_result:
#                     logging.info("it got to upload_images")
#                     new_picture = "{}_test.jpg".format(str(request.user))
#                     result = recognize(str(student.picture), new_picture) 
                    

#                     if (result > 80):
#                         attendance = AttendanceModel.objects.get(id=pk)
                        
#                         if (attendance.is_active == False):
#                             return Response({"errors": ["Attendance taking has ended"]}, status=status.HTTP_400_BAD_REQUEST)                    
                        
#                         if (student in attendance.present_students.all()):
#                             return Response({"errors": ["Your attendance has already been taken"]}, status=status.HTTP_400_BAD_REQUEST)

#                         attendance.present_students.add(student)
#                         attendance.save()
#                         return Response({'message': 'You have been marked present' ,'similarity': "{}%".format(result)}, status=status.HTTP_200_OK)

#                     return Response({"errors": ["Facial recognition test failed"]}, status=status.HTTP_400_BAD_REQUEST)                    

#                 return Response({"errors": ["An error occured. Take picture again"]}, status=status.HTTP_400_BAD_REQUEST)

#             return Response({"errors": ["Picture was not sent"]}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({"errors": ["student not registered"]}, status=status.HTTP_400_BAD_REQUEST)
        

class CreateVenue(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if Teacher.objects.get(user = request.user):
            teacher = Teacher.objects.get(user=request.user)

            try:
                lat = request.data.get('latitude', '')
                long = request.data.get('longitude', '')
                name = request.data.get('name', '')
                radius = request.data.get('radius', '')
            except:
                return Response({"errors": ["parameters required are not complete"]}, status=status.HTTP_400_BAD_REQUEST)

            try:
                venue = VenueModel.objects.create(name=name, position="{},{}".format(lat, long), radius=radius)    
            except:
                return Response({"errors": ["Error occured in creating venue, try again"]}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'key': venue.pk ,'message': 'Venue successfully created'}, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        if Teacher.objects.get(user = request.user):
            teacher = Teacher.objects.get(user=request.user)

            try:
                lat = request.data.get('latitude', '')
                long = request.data.get('longitude', '')
                name = request.data.get('name', '')
                radius = request.data.get('radius', '')
            except:
                return Response({"errors": ["parameters required are not complete"]}, status=status.HTTP_400_BAD_REQUEST)

            try:
                if VenueModel.objects.get(pk=pk):
                    venue = VenueModel.objects.get(pk=pk)
                    venue.name = name
                    venue.position = "{},{}".format(lat, long)
                    venue.radius = radius
                    venue.save()    
            except:
                return Response({"errors": ["Error occured in creating venue, try again"]}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'key': venue.pk ,'message': 'Venue {} successfully updated'.format(venue.name)}, status=status.HTTP_200_OK)

class Attendance(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if Teacher.objects.get(user = request.user):
            
            teacher = Teacher.objects.get(user=request.user)
            
            if (request.data.get('attendance', '')):
                attendance = request.data.get('attendance')
                if (AttendanceModel.objects.get(pk=attendance)):
                    attendance  = AttendanceModel.objects.get(pk=attendance)
                    if (request.data.get('is_active', '')):
                        is_active = request.data.get('is_active')
                        attendance.is_active = is_active
                        attendance.save()
                        return Response({'message': 'Attendance has successfully been stopped'}, status=status.HTTP_200_OK)
                else:
                    return Response({"errors": ["Attendance key sent is invalid"]}, status=status.HTTP_400_BAD_REQUEST)

            try:
                name = request.data.get('name', '')
                course = request.data.get('course', '')
                venue = request.data.get('venue', '')
                is_active = request.data.get('is_active', '')
            except:
                return Response({"errors": ["parameters required are not complete"]}, status=status.HTTP_400_BAD_REQUEST)

            if Course.objects.get(pk=course):
                
                course = Course.objects.get(pk=course)
                if course in teacher.course_set.all():
                    if Venue.objects.get(pk=venue):
                        venue = Venue.objects.get(pk=venue)
                        
                        if is_active in ["true", "True", True]:
                            attendance = AttendanceModel.objects.create(name=name, venue= venue, course=course, is_active=True)
                            print("it got here")
                            return Response({'key': attendance.pk ,'message': 'Attendance has successfully been created'}, status=status.HTTP_200_OK)
                        else:
                            return Response({"errors": ["set is_active to True"]}, status=status.HTTP_400_BAD_REQUEST)                        
                    else:
                        return Response({"errors": ["Venue code entered is invalid"]}, status=status.HTTP_400_BAD_REQUEST)    
                else:
                    return Response({"errors": ["You cannot start attendance for a course that isn't yours"]}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({"errors": ["Course code entered is invalid"]}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"errors": ["Account does not belong to a teacher"]}, status=status.HTTP_400_BAD_REQUEST)