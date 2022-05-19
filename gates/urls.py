from django.urls import path
from .views import upsert_member, start


urlpatterns = [
    path('upsertmember', upsert_member, name='upsert_member'),
    path('start', start, name='start')
]
