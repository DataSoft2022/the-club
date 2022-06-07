from django.contrib import admin
from .models import ZKDevice, Gate, LogHistory, FaildMember, FaildTimezone

admin.site.register(Gate)
admin.site.register(ZKDevice)
admin.site.register(LogHistory)
admin.site.register(FaildMember)
admin.site.register(FaildTimezone)
