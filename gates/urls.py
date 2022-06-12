from django.urls import path
from . import views 

urlpatterns = [
    path('addmembers', views.add_members, name='add_members'),
    path('addstudent', views.add_student, name='add_student'),
    # path('resettimetable', views.reset_timetable, name='reset_timetable'),
    path('live', views.live, name='live'),
    path('insertgate', views.insert_gate, name='insertgate'),
    path('deletegate', views.delete_gate, name='deletegate'),
    path('updategate', views.update_gate, name='updategate'),
    path('insertzk', views.insert_zk_device, name='insertzk'),
    path('deletezk', views.delete_zk_device, name='deletezk'),
    path('updatezk', views.update_zk_device, name='updatezk'),
]
