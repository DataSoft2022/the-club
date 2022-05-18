import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ZKDevice

@csrf_exempt
def add_member(request):
    # body = json.loads(request.body)
    # zk_devices = ZKDevice.objects.all()
    
    # for zk in zk_devices:
    #     connstr = f'protocol=TCP,ipaddress={zk.ip},port={zk.port},timeout=4000,passwd={zk.passwd}'
    # cards = body.get('data')
    # print(cards)
    return HttpResponse(json.dumps({'result': 'pass'}))

