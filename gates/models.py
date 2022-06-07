from django.db import models

# connstr = 'protocol=TCP,ipaddress=192.168.1.201,port=4370,timeout=4000,passwd='
class Gate(models.Model):
    name = models.CharField(max_length=30, null=False)
    active = models.BooleanField(default = False)

    def __str__(self):
        return self.name

class ZKDevice(models.Model):
    gate = models.ForeignKey(Gate, on_delete=models.CASCADE)
    ip = models.CharField(max_length=20)
    port = models.CharField(max_length=5)
    passwd = models.CharField(max_length=100,  blank=True)
    
    def __str__(self):
        return self.ip


class LogHistory(models.Model):
    gate = models.ForeignKey(Gate, on_delete=models.CASCADE)
    zk_device = models.ForeignKey(ZKDevice, on_delete=models.CASCADE)
    card = models.CharField(max_length=15)
    pin = models.CharField(max_length=15)
    time = models.DateTimeField()

    def __str__(self):
        return f"Gate: {self.gate}-------Card: {self.card}---------Time: {str(self.time)}"
    


class FaildMember(models.Model):
    cat = [("Student", "Student"),
           ("Member", "Member")]
    zk_device = models.ForeignKey(ZKDevice, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=cat)
    card = models.CharField(max_length=15)
    pin = models.CharField(max_length=15)
    start_date =  models.CharField(max_length=10)
    end_date = models.CharField(max_length=10)

    def __str__(self):
        return f"type: {self.category} ---- zk: {self.zk_device.ip} ----- start: {self.start_date} ---- end: {self.end_date} ---- pin: {self.pin}"


class FaildTimezone(models.Model):
    member = models.ForeignKey(FaildMember, on_delete=models.CASCADE)
    day = models.IntegerField()
    time = models.CharField(max_length=8)

    def __str__(self):
        return f"{self.member.id} ------ day: {self.day} ----- time: {self.time}"
