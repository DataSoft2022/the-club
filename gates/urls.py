from django.urls import path
from . import views 

urlpatterns = [
    path('upsertmember', views.upsert_member, name='upsert_member'),
    path('upsertstudent', views.upsert_student, name='upsert_student'),
    # path('resettimetable', views.reset_timetable, name='reset_timetable'),
    path('start', views.start, name='start')
]
