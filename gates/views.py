import json
import time
from threading import Thread
import datetime as dt
from datetime import datetime
from pyzkaccess import ZKAccess, User, UserAuthorize, Timezone
from django.views.decorators.csrf import csrf_exempt
from .models import ZKDevice, Gate, FaildMember, FaildTimezone
from .zk_api import upsert_user, upsert_auth, reset_timezone, live_capture
from rest_framework.response import Response
from rest_framework.decorators import api_view

            
@api_view(['POST'])  
@csrf_exempt
def upsert_member(request):
    """activate cards on every zk device by taking a list of dicts contains
    cards, start date and end date and timezone
    request body the following
    { 'cards' :
        [
            {
                card_no: (int) card number
                start_date: (datetime-isoformat) starting date of the card 
                end_date: (datetime-isoformat) ending date of the card
                timezone: (int) timezone id !Hint: to enable all times timezone=1
                pin: (int) pin number
            }
        ]
    response
        json object {
                        'success': True || False,
                        'message': list of error messages in case success=False
                    }
    """

    body = request.data
    data = body.get('cards')
    device_id = body.get('device')
    if not device_id:
        zk_devices = ZKDevice.objects.all()
    else:
        zk_devices = ZKDevice.objects.filter(id=device_id)
    response = {'message': []}
    
    for zk_device in zk_devices:
        connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
        try:
            zk = ZKAccess(connstr=connstr)
            for d in data:
                card = d['card_no']
                pin = d['pin']
                start_date = datetime.fromisoformat(d['start_date'])
                end_date = datetime.fromisoformat(d['end_date'])
                upsert_user(zk, card, pin, start_date, end_date)
                upsert_auth(zk, pin)

                exist = FaildMember.objects.filter(zk_device=zk_device, pin=d['pin']).exists()
                if exist:
                    FaildMember.objects.get(zk_device=zk_device, pin=d['pin']).delete()
        except:
            response['message'].append(f"can't connect to {zk_device.gate.name} with device {zk_device.ip}")
            for d in data:
                exist = FaildMember.objects.filter(zk_device=zk_device, pin=d['pin']).exists()
                if not exist:
                    member = FaildMember.objects.create(zk_device=zk_device,
                                                        category="Member",
                                                        card=d['card_no'],
                                                        pin=d['pin'],
                                                        start_date=d['start_date'],
                                                        end_date=d['end_date'])
                    member.save()
                
       
    response['success'] = len(response['message']) == 0
    return Response(response)  



@api_view(['POST'])
@csrf_exempt
def upsert_student(request):
    """create new user and set authorization to set of time zones sent by user
        request: json object contains the following:
                {
                    "card": (dict) contains card details (card_no, pin, start_date, end_date),
                    "schedule": (list) contains list of lists where each list represent [day number, time] 
                                ex: [3, "17:00:00"] !hint: time should be on isoformat form
                                week days represented as following: Sunday = 1, Monday = 2, .... .
                }
    """
    body = request.data
    card = body.get('card')
    schedule = body.get('schedule')
    device_id = body.get('device')
    response = {'message': []}
    if device_id:
        zk_devices = ZKDevice.objects.filter(id=device_id)
    else:
        zk_devices = ZKDevice.objects.all()
        
    for zk_device in zk_devices:
        connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
        try:
            zk = ZKAccess(connstr=connstr)
            start_date = datetime.fromisoformat(card['start_date'])
            end_date = datetime.fromisoformat(card['end_date']) + dt.timedelta(1)
            upsert_user(zk, card['card_no'], card['pin'], start_date, end_date)
        
            for day, time in schedule:
                h = int(time.split(':')[0])
                timezone_id = int(day) * 100 + h
                upsert_auth(zk, card['pin'], timezone_id)
        except:
            response['message'].append(f"can't connect to {zk_device.gate.name} with device {zk_device.ip}")
            exist = FaildMember.objects.filter(zk_device=zk_device, pin=card['pin']).exists()
            if not exist:
                 member = FaildMember.objects.create(zk_device=zk_device,
                                                        category="Student",
                                                        card=card['card_no'],
                                                        pin=card['pin'],
                                                        start_date=card['start_date'],
                                                        end_date=card['end_date'])
                 member.save()
                 for day, time in schedule:
                     timezone = FaildTimezone(member=member, day=day, time=time)
                     timezone.save()
        
            

    response['success'] = len(response['message']) == 0

    return Response(response)

@api_view(['POST'])  
@csrf_exempt
def live(request):
    """
    send gate name and task = (activate, deactivate)
    {
    "gate" = "Gate 4",
    "task" = "activate"
    }
    """
    body = request.data
    try:
        gate = Gate.objects.get(name= body.get('gate'))
    except Exception as e:
        return Response({
            'success': False
        })
    
    task = body.get('task')
    if task == 'deactivate':
        try:
            gate.active = False
            gate.save()
            return Response({'success': True})
        except:
            return Response({'success': False})
        
    if gate.active:
        return Response ({'success': True, 'message': 'Gate already active'})

    try:
        gate.active = True
        gate.save()
        devices = gate.zkdevice_set.all()
        for d in devices:
            live_capture(gate.id, d)
            # t = Thread(target=live_capture, args=[gate.id, d])
            # t.start()
    except Exception as e:
        print(e)
        return Response({
            'success': False
        })

    return Response({
        'success': True
    })

