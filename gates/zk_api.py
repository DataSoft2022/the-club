import datetime as dt
from datetime import datetime
from pyzkaccess import ZKAccess, User, UserAuthorize, Timezone, Transaction
from .models import ZKDevice, Gate, LogHistory, FaildMember, FaildTimezone
from threading import Thread

def upsert_user(zk, card, pin, start_date, end_date):
    """
        insert new user into user table
    """
    my_user = User(card=str(card), pin=str(pin),
                           start_time=start_date, end_time=end_date)
    zk.table(User).upsert(my_user)


def upsert_auth(zk, pin, timezone=1):
    """
        insert new user into UserAuthorize table, default timezone to 1
        where 1 is timezone creating to enable user 24 hours per day
    """
    auth_user = UserAuthorize(pin=str(pin), doors = (1, 1, 1, 1), timezone_id=timezone)
    zk.table(UserAuthorize).upsert(auth_user)


def connect_zk(zk_device):
    connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
    try:
        return ZKAccess(connstr=connstr)
    except:
        raise Exception(f"Can't connect t device {zk_device}")

    
def reset_timezone(zk):
    """
        clear timezone table and insert new one as following:
        timezone_id : will 3 digit int where the hundreds will represent week days
                      1 = sunday, 2 = monday, ...., 7 = saturday,
                      and the other two represt time hours ex: 18 equivalent to 6 PM.
        the id = 1 is saved for 24 hours time zone
    """
    # for t in zk.table(Timezone):
        # t.delete()
    st = datetime.time(0, 0, 0)
    et = datetime.time(23, 59, 59)
    defautl_t = Timezone(timezone_id='1', sun_time1 = (st, et), mon_time1=(st, et), tue_time1=(st, et), 
                        wed_time1=(st, et), thu_time1=(st, et), fri_time1=(st, et), sat_time1=(st, et))
    zk.table(Timezone).upsert(defautl_t)
    after_12_s = datetime.time(0, 0, 0)
    after_12_e = datetime.time(2, 0, 0)
    for d in range(100, 800, 100):
        for t in range(6, 24):
            st = datetime.time(t, 0, 0)
            et = datetime.time(23, 59, 59)
            if d == 100:
                time_zone = Timezone(timezone_id=str(d+t), sun_time1=(st, et), 
                                     mon_time1=(after_12_s, after_12_e))
            elif d == 200:
                time_zone = Timezone(timezone_id=str(d+t), mon_time1=(st, et), 
                                     tue_time1=(after_12_s, after_12_e))
            elif d == 300:
                time_zone = Timezone(timezone_id=str(d+t), tue_time1=(st, et), 
                                     wed_time1=(after_12_s, after_12_e))
            elif d == 400:
                time_zone = Timezone(timezone_id=str(d+t), wed_time1=(st, et), 
                                     thu_time1=(after_12_s, after_12_e))
            elif d == 500:
                time_zone = Timezone(timezone_id=str(d+t), thu_time1=(st, et), 
                                     fri_time1=(after_12_s, after_12_e))
            elif d == 600:
                time_zone = Timezone(timezone_id=str(d+t), fri_time1=(st, et), 
                                     sat_time1=(after_12_s, after_12_e))
            else:
                time_zone = Timezone(timezone_id=str(d+t), sat_time1=(st, et), 
                                     sun_time1=(after_12_s, after_12_e))
            
            zk.table(Timezone).upsert(time_zone)
        print(d)


        

def reset_all_zk_timezone():
    """reset timezone to custom table created by reset_timezone function
    """
    for zk_device in ZKDevice.objects.all():
        connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
        try:
            zk = ZKAccess(connstr=connstr)
        except:
            raise Exception(f"can't connect to device {zk_device.ip}")
            
        reset_timezone(zk)
    return 'done'


def upsert_members(cards, device_id=''):
    
    """activate cards on every zk device by taking a list of dicts contains
    cards, start date and end date and timezone
    The body has the following
    {
    'cards' :
        [
            {
                card_no: (int) card number
                start_date: (datetime-isoformat) starting date of the card 
                end_date: (datetime-isoformat) ending date of the card
                pin: (int) pin number
            }
        ],
    'device': 'device_id' !hint: if none get all devices
    }
    response
        json object {
                        'success': True || False,
                        'message': list of error messages in case success=False
                    }
    """
    flag = 0
    
    if not device_id:
        zk_devices = ZKDevice.objects.all()
    else:
        zk_devices = ZKDevice.objects.filter(id=device_id)
    response = {'message': []}

    for zk_device in zk_devices:
        try:
            if zk_device.gate.active:
                toggle_gate(zk_device.gate.name, 'deactivate')
                flag = 1
                
            zk = connect_zk(zk_device)
            for c in cards:
                card = c['card_no']
                pin = c['pin']
                start_date = datetime.fromisoformat(c['start_date'])
                end_date = datetime.fromisoformat(c['end_date'])
                upsert_user(zk, card, pin, start_date, end_date)
                upsert_auth(zk, pin)
                exist = FaildMember.objects.filter(zk_device=zk_device, pin=c['pin']).exists()
                if exist:
                    FaildMember.objects.get(zk_device=zk_device, pin=c['pin']).delete()
            if flag:
                toggle_gate(zk_device.gate.name, 'activate')
                flag  = 0
        except:
            response['message'].append(f"can't connect to {zk_device.gate.name} with device {zk_device.ip}")
            for c in cards:
                exist = FaildMember.objects.filter(zk_device=zk_device, pin=c['pin']).exists()
                if not exist:
                    member = FaildMember.objects.create(zk_device=zk_device,
                                                        category="Member",
                                                        card=c['card_no'],
                                                        pin=c['pin'],
                                                        start_date=c['start_date'],
                                                        end_date=c['end_date'])
                    member.save()
                
        
    response['success'] = len(response['message']) == 0
    return response



def upsert_student(card, schedule, device_id=''):
    """create new user and set authorization to set of time zones sent by user
        request: json object contains the following:
                {
                    "card": (dict) contains card details (card_no, pin, start_date, end_date),
                    "schedule": (list) contains list of lists where each list represent [day number, time] 
                                ex: [3, "17:00:00"] !hint: time should be on isoformat form
                                week days represented as following: Sunday = 1, Monday = 2, .... .
                }
    """

    response = {'message': []}
    flag = 0
    
    if device_id:
        zk_devices = ZKDevice.objects.filter(id=device_id)
    else:
        zk_devices = ZKDevice.objects.all()
        
    for zk_device in zk_devices:
        try:
            if zk_device.gate.active:
                toggle_gate(zk_device.gate.name, 'deactivate')
                flag = 1
                
            zk = connect_zk(zk_device)
            start_date = datetime.fromisoformat(card['start_date'])
            end_date = datetime.fromisoformat(card['end_date']) + dt.timedelta(1)
            upsert_user(zk, card['card_no'], card['pin'], start_date, end_date)

            for day, time in schedule:
                h = int(time.split(':')[0])
                timezone_id = int(day) * 100 + h
                upsert_auth(zk, card['pin'], timezone_id)
                
            exist = FaildMember.objects.filter(zk_device=zk_device, pin=card['pin']).exists()
            if exist:
                FaildMember.objects.get(zk_device=zk_device, pin=card['pin']).delete()

            if flag:
                toggle_gate(zk_device.gate.name, 'activate')
                flag = 0
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

    return response



def send_data(pin):
    #api_secret = aad79b7ba227ba9
    #api_key = fdc04965d6f8c41

    import requests
    import json

    url = "http://develop.test:8000/api/method/gates.api.add_member"

    payload = json.dumps({
        "pin": pin
    })
    headers = {
        'Authorization': 'token fdc04965d6f8c41:aad79b7ba227ba9',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def live_capture(gate_id, zk_device):

    zk= connect_zk(zk_device)
    try:
        print("connect to zk", zk.parameters.ip_address)
        zk.relays.lock.switch_on(5)
        while Gate.objects.filter(id=gate_id)[0].active:
            for door1_event in zk.doors[0].events.poll(timeout=5):
                print(door1_event)
                if door1_event.card and door1_event.card != '0':
                    print('Got card #', door1_event.card)
                    #send_data(pin)
                print("waiting card")
        print("out man")
    except:
        raise Exception(f"can't connect to device {zk_device.ip}")



def toggle_gate(gate, task):
    try:
        gate = Gate.objects.get(name=gate)
   
        if task == 'deactivate':
            gate.active = False
            gate.save()
            return {'success': True}
        if gate.active:
            return {'success': True, 'message': 'Gate already active'}

        gate.active = True
        gate.save()
        devices = gate.zkdevice_set.all()
        for d in devices:
            # live_capture(gate.id, d)
            t = Thread(target=live_capture, args=[gate.id, d])
            t.start()
    except Exception as e:
        return {'success': False}

    return {'success': True}
