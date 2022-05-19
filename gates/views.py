import json
from datetime import datetime
from pyzkaccess import ZKAccess, User
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ZKDevice

@csrf_exempt
def add_member(request):
    body = json.loads(request.body)
    cards = body.get('cards')
    start_date = datetime.fromisoformat(body.get('start_date'))
    end_date = datetime.fromisoformat(body.get('end_date'))
    zk_devices = ZKDevice.objects.all()
    for zk in zk_devices:
        try:
            connstr = f'protocol=TCP,ipaddress={zk.ip},port={zk.port},timeout=4000,passwd={zk.passwd}'
            print(connstr)
            zk = ZKAccess(connstr=connstr)
            for card in cards:
                c = zk.table(User).count() + 1
                my_user = User(card=str(card), pin=str(c),
                                start_time=start_date, end_time=end_date,
                                super_authorize=False)
                zk.table(User).upsert(my_user)
        except:
            return HttpResponse(json.dumps({'success': False}))
    return HttpResponse(json.dumps({'result': True}))    

@csrf_exempt
def start(request):
    return HttpResponse(json.dumps({'id':'done'}))
