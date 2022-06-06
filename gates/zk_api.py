import json
import datetime
from pyzkaccess import ZKAccess, User, UserAuthorize, Timezone
from .models import ZKDevice, Gate
import time


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


#api_secret = aad79b7ba227ba9
#api_key = fdc04965d6f8c41

        
def live_capture(gate_id, zk_device):
     connstr = f'protocol=TCP,ipaddress={zk_device.ip},port={zk_device.port},\
                    timeout=4000,passwd={zk_device.passwd}'
     try:
        zk = ZKAccess(connstr=connstr)
        print("connect to zk", zk.parameters.ip_address)
        zk.relays.lock.switch_on(5)
        while Gate.objects.filter(id=gate_id)[0].active:
            for door1_event in zk.doors[0].events.poll(timeout=5):
                print(door1_event)
                if door1_event.card and door1_event.card != '0':
                    print('Got card #', door1_event.card)
                    send_data()
                print("waiting card")
        print("out man")
     except:
         raise Exception(f"can't connect to device {zk_device.ip}")


def send_data():
    import requests
    import json

    url = "http://103.136.40.46:72/api/resource/Gates"

    payload = json.dumps({
        "data": {
            "num": 23234
        }
    })
    headers = {
        'Authorization': 'token fdc04965d6f8c41:aad79b7ba227ba9',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)



def get_history():
   print("hi i started")

def play_with():
    print("playing")
    
