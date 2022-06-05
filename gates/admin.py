from django.contrib import admin
from .models import ZKDevice, Gate

admin.site.register(Gate)
admin.site.register(ZKDevice)
