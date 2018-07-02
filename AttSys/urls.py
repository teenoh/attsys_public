"""AttSys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from server.views import VerifyPicture, LoginViewSet, StudentViewSet, Attendance, TeacherViewSet, CreateVenue
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("login", LoginViewSet, base_name="login")
router.register('student', StudentViewSet, base_name="student")
router.register('teacher', TeacherViewSet, base_name="teacher")

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^verify_pic/', VerifyPicture.as_view()),
    url(r'^attendance_ish/', Attendance.as_view()),
    url(r'^venue_ish/(?P<pk>[0-9]+)/$', CreateVenue.as_view()),
    url(r'', include(router.urls))
]
