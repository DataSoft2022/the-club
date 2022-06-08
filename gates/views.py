from threading import Thread
from django.views.decorators.csrf import csrf_exempt
from .zk_api import live_capture, upsert_members, upsert_student, toggle_gate
from rest_framework.response import Response
from rest_framework.decorators import api_view

            
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
