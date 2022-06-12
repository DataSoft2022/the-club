from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .zk_api import live_capture, upsert_members, upsert_student, toggle_gate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Gate, ZKDevice

            
@api_view(['POST'])  
@csrf_exempt
def add_members(request):
    body = request.data
    cards = body.get('cards')
    device_id = body.get('device_id')
    resp = upsert_members(cards, device_id)
    return Response(resp)





@api_view(['POST'])
@csrf_exempt
def add_student(request):
    body = request.data
    card = body.get('card')
    schedule = body.get('schedule')
    device_id = body.get('device_id')
    resp = upsert_student(card, schedule, device_id)
    return Response(resp)



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
    resp = toggle_gate(body.get("gate"), body.get("task"))
    return Response(resp)



@api_view(['POST'])
@csrf_exempt
def insert_gate(request):
    body = request.data
    name = body.get("gate")
    try:
        gate = Gate.objects.create(name=name)
        gate.save()
        return Response({'success': True})
    except:
        return Response({'success': False})



@api_view(['POST'])
@csrf_exempt
def update_gate(request):
    body = request.data
    try:
        gate = get_object_or_404(Gate, name=body.get('old_name'))
        if body.get('name'):
            gate.name = body.get('name')
        gate.save()
        return Response({'success': True})
    except:
        return Response({'success': False})


@api_view(['POST'])
@csrf_exempt
def delete_gate(request):
    body = request.data
    name = body.get('gate')
    try:
        gate = get_object_or_404(Gate, name=name)
        gate.delete()
        return Response({'success': True})
    except:
        return Response({'success': False})


@api_view(['POST'])
@csrf_exempt
def insert_zk_device(request):
    body = request.data
    ip = body.get('ip')
    port = body.get('port')
    passwd = body.get('passwd')

    try:
        gate = get_object_or_404(Gate, name=body.get('gate'))
        zk_device = ZKDevice.objects.create(gate=gate, ip=ip, port=port, passwd=passwd)
        zk_device.save()
        return Response({"success": True})
    except:
        return Response({"success": False})


@api_view(['POST'])
@csrf_exempt
def delete_zk_device(request):
    body = request.data
    try:
        zk_device = get_object_or_404(ZKDevice, ip=body.get('ip'))
        zk_device.delete()
        return Response({'success': True})
    except:
        return Response({'success': False})


@api_view(['POST'])
@csrf_exempt
def update_zk_device(request):
    body = request.data
    zk_device = get_object_or_404(ZKDevice, ip=body.get('old_ip'))
    try:

        if body.get('ip'):
            zk_device.ip = body.get('ip')
            
        if body.get('gate'):
            gate = get_object_or_404(Gate, name=body.get('gate'))
            zk_device.gate = gate

        if body.get('port'):
            zk_device.port = body.get('port')

        if body.get('passwd'):
            zk_device.passwd = body.get('passwd')

        zk_device.save()
        return Response({'success': True})
    except:
        return Response({'success': False})
