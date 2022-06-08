from apscheduler.schedulers.background import BackgroundScheduler
from .zk_api import upsert_members, upsert_student
from .models import ZKDevice, Gate, LogHistory, FaildMember, FaildTimezone

def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(get_history, 'interval', hours=12)
    scheduler.add_job(testing_print, 'interval', seconds=5)
    scheduler.add_job(failed_upserting, 'interval', seconds=30)
    # scheduler.start()


def testing_print():
    print("loading.....")


def get_history():
    print("start syncing")
    zks_devices = ZKDevice.objects.all()
    for zk_device in zks_devices:
        gate = ZKDevice.objects.get(id=zk_device.id).gate
        zk = connect_zk(zk_device)
        log = zk.table(Transaction)
        for l in log:
            history = LogHistory.objects.create(gate = gate,
                                                zk_device = zk_device,
                                                card = l.card,
                                                pin = l.pin,
                                                time = l.time)
            try:
                history.save()
                # l.delete()
            except:
                print("error")
                pass
        
    print("syncing done")
    return {'success': True}


def failed_upserting():
    zk_devices = ZKDevice.objects.all()
    for zk_device in zk_devices:
        members = FaildMember.objects.filter(zk_device=zk_device, category="Member")
        request = {}
        cards = []
        for member in members:
             cards.append({
                 'card_no': member.card,
                 'start_date': member.start_date,
                 'end_date': member.end_date,
                 'pin': member.pin
             })
        device_id = zk_device.id
        resp = upsert_members(cards, device_id=device_id)
        if not resp:
            continue
        students =  FaildMember.objects.filter(zk_device=zk_device, category="Student")
        for student in students:
            request = {}
            device_id = zk_device.id
            card = {
                'card_no': student.card,
                'pin': student.pin,
                'start_date': student.start_date,
                'end_date': student.end_date
            }
            schedule = []
            for timezone in FaildTimezone.objects.filter(member=student):
                schedule.append([timezone.day, timezone.time])
            resp = upsert_student(card, schedule, device_id=device_id)
            if not resp['success']:
                break
        
