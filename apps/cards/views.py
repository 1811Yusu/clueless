from typing import Tuple
from django.views.generic.base import RedirectView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Pin, Save, History, Comment
from apps.user.models import User
from .serializers import CommentPostSerializer, CommentSerializer, PinSerializer, PinCreateSerializer, UserAvatarSerializer, PinSaveSerializer, HistoryPostSerializer, HistoryGetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@api_view(['GET'])
def api_status(request):
    return Response(data={"message": "api is working"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def home(request: Request):
    pins = Pin.objects.all().order_by("-created_at")
    serializer = PinSerializer(pins, many=True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(methods=['POST'], request_body=PinCreateSerializer)
@api_view(['GET','POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_pin(request):
    if request.method == 'GET':
        user = request.user
        seralizer = UserAvatarSerializer(instance=user)
        return Response(data=seralizer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = {
            'title': request.data.get('title'),
            'description': request.data.get('description'),
            'image': request.data.get('image'),
            'creator': request.user,
            'website': request.data.get('website'),
        }
        new_pin = PinCreateSerializer(data=data)
        if new_pin.is_valid():
            new_pin.save()
            return Response(new_pin.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=new_pin.errors)
@swagger_auto_schema(method='POST', request_body=PinSaveSerializer)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save_pin(request: Request):

    if request.method == 'POST':
        data = {
            'pin': request.data.get('pin'),
            'user': request.user.id,
        }
        saved_pin = PinSaveSerializer(data=data)
        if saved_pin.is_valid():
            saved_pin.save()
            return Response(saved_pin.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=saved_pin.errors)

@swagger_auto_schema(methods=['POST'], query_serializer=HistoryPostSerializer)
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def history(request: Request):
    if request.method == "POST":
        user = request.user.id
        pin = request.data.get('pin')
        print(user, pin)
        ser_pin = HistoryPostSerializer(data={'user': user, 'pin': pin})
        if ser_pin.is_valid():
            ser_pin.save()
        else:
            return Response(data=ser_pin.errors)
        return Response(data=ser_pin.data, status=status.HTTP_201_CREATED)
    else:
        history_pins = History.objects.filter(user=request.user.id)
        ser_pin = HistoryGetSerializer(instance=history_pins, many=True)
        return Response(data=ser_pin.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_history(request: Request, **kwargs):
    if request.method == "DELETE":
        id = kwargs.get('id')
        History.objects.filter(pk=id).delete()
        return Response({'msg':"Pin Deleted From History"}, status=status.HTTP_201_CREATED)


from .serializers import PinCommentSerializer
from apps.user.serializers import UserSerializer
@swagger_auto_schema(method='POST', query_serializer=CommentPostSerializer)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_comments(request: Request, pin_id):
    pin = Pin.objects.filter(pk=pin_id).first()
    if pin == None:
        return Response({"msg": "pin not found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        try:
            p = PinCommentSerializer(pin)
            return Response({'comment_list':p.data["comment_set"] }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'msg':str(e) }, status=status.HTTP_404_NOT_FOUND)

    elif request.method == "POST":
        try:
            data = {
                "creator" :request.user.id,
                "pin": pin_id,
                "content": request.data.get("content"),
                "reactee": [request.user.id,]
            }
            new_comment = CommentPostSerializer(data=data)
            if new_comment.is_valid():
                new_comment.save()
                return Response({'msg':new_comment.data }, status=status.HTTP_201_CREATED)
            else:
                return Response({'msg': new_comment.errors }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg':str(e) }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def react_comment(request: Request, comment_id):
    comment = Comment.objects.filter(pk=comment_id).first()
    if comment == None:
        return Response({"msg": "comment not found"}, status=status.HTTP_404_NOT_FOUND)
    user_id = request.user.id
    reactions = comment.reactions
    if user_id in reactions:
        reactions.remove(user_id)
    else:
        reactions.append(user_id)
        comment.reactions = reactions
        comment.save()
        serializer = CommentSerializer(instance=comment)
    return Response(serializer.data, status=status.HTTP_200_OK)