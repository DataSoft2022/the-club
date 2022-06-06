from django.contrib import admin
from .models import ZKDevice, Gate, LogHistory

admin.site.register(Gate)
admin.site.register(ZKDevice)
admin.site.register(LogHistory)
