import json
import datetime
from pyzkaccess import ZKAccess, User, UserAuthorize, Timezone
from .models import ZKDevice


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
    for t in zk.table(Timezone):
        t.delete()
    defautl_t = Timezone(timezone_id='1')
    zk.table(Timezone).upsert(defautl_t)
    after_12_s = datetime.time(0, 0, 0)
    after_12_e = datetime.time(2, 0, 0)
    for d in range(100, 800, 100):
        for t in range(6, 24):
            st = datetime.time(t, 0, 0)
            et = datetime.time(23, 59, 0)
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