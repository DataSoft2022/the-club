from django.urls import path
from .views import add_member


urlpatterns = [
    path('addmember', add_member, name='add_member')
]
