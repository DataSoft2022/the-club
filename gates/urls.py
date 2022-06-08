from django.urls import path
from . import views 

urlpatterns = [
    path('addmembers', views.add_members, name='add_members'),
    path('addstudent', views.add_student, name='add_student'),
    # path('resettimetable', views.reset_timetable, name='reset_timetable'),
    path('live', views.live, name='live')
]
