from django.urls import path
from .views import add_member, start


urlpatterns = [
    path('addmember', add_member, name='add_member'),
    path('start', start, name='start')
]
