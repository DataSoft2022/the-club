import json
from datetime import datetime
from pyzkaccess import ZKAccess, User, UserAuthorize
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ZKDevice


def print_cards(table):
    zk_devices = ZKDevice.objects.all()
    for zk_device in zk_devices:
        connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
        zk = ZKAccess(connstr=connstr)
        for u in zk.table(table):
            print(u)
            
def clear_cards(table):
    
    zk_devices = ZKDevice.objects.all()
    for zk_device in zk_devices:
        connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
        zk = ZKAccess(connstr=connstr)
        for u in zk.table(table):
            u.delete()
        
@csrf_exempt
def upsert_member(request):
    """
    activate cards on every zk device by taking a list of dicts contains
    cards, start date and end date and timezone
    request body the following
    { 'data' :
        [
            {
                cards: (int) card number
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
    curl example:
        curl -X POST 'http://127.0.0.1:8000/gates/addmember'
        --data '{"cards": ['231', '12312'], "start_date": "2022-03-12", "end_date":"2023-02-12"}'
        --header  'Content-Type: application/json'

        response:
            {
                'success': True,
                'message': []
            }
    """

    body = json.loads(request.body)
    data = body.get('data')
    zk_devices = ZKDevice.objects.all()
    response = {'message': []}
    
    for zk_device in zk_devices:
        connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
        try:
            zk = ZKAccess(connstr=connstr)
        except:
            response['message'].append(f"can't connect to {zk_device.ip}")
            continue

        for d in data:
            card = d['card']
            pin = d['pin']
            start_date = datetime.fromisoformat(d['start_date'])
            end_date = datetime.fromisoformat(d['end_date'])
            try:            
                upsert_user(zk, card, pin, start_date, end_date)
                upsert_auth(zk, pin)
            except:
                response['message'] = 'make sure the data is correct'
                response['success'] = False
                return JsonResponse(response)

    if len(response['message']) > 0:
        response['success'] = False
    else:
        response['success'] = True
    return JsonResponse(response)  


def upsert_user(zk, card, pin, start_date, end_date):
        my_user = User(card=str(card), pin=str(pin),
                               start_time=start_date, end_time=end_date)
        zk.table(User).upsert(my_user)


def upsert_auth(zk, pin, timezone=1):
    auth_user = UserAuthorize(pin=str(pin), doors = (1, 1, 1, 1), timezone_id=timezone)
    zk.table(UserAuthorize).upsert(auth_user)

    
@csrf_exempt
def start(request):
    return HttpResponse(json.dumps({'id':'done'}))
