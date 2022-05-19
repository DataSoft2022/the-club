from django.db import models

# connstr = 'protocol=TCP,ipaddress=192.168.1.201,port=4370,timeout=4000,passwd='
class Gates(models.Model):
    name = models.CharField(max_length=30, null=False)

    def __str__(self):
        return self.name

class ZKDevice(models.Model):
    gate = models.ForeignKey(Gates, on_delete=models.CASCADE)
    ip = models.CharField(max_length=20)
    port = models.CharField(max_length=5)
    passwd = models.CharField(max_length=100,  blank=True)
    
    def __str__(self):
        return self.ip
