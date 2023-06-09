
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.authtoken.models import Token
from .serializers import UserSignUpSerializer, UserSerializer, UserBoard, UserBoardPin, UserProfile, BoardSerializer
from rest_framework.renderers import JSONRenderer
from apps.user.models import User
from apps.cards.models import Pin
import http.client
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def example_view(request: Request, format="json"):
    content = { 'user': str(request.user), 'auth': str(request.auth), }
    return Response(content)


@swagger_auto_schema(method='POST', query_serializer=UserSignUpSerializer)
@permission_classes([])
@api_view(['POST'])
def sign_up(request: Request):
    data = {'data': '',  'status': ''}
    user_serialized = UserSignUpSerializer(data=request.data)
    if user_serialized.is_valid():
        user_serialized.save()
        data['data'] = {
            'user': {
                "username": user_serialized.data.get('username'),
                "email": user_serialized.data.get('email')
            },
            "token" : Token.objects.get(user__username=user_serialized.data.get('username')).key,
            'message': 'Created'
            }
        data['status'] = status.HTTP_200_OK
    else:
        data['data'] = user_serialized.errors
        data['status'] = status.HTTP_403_FORBIDDEN
    return Response(**data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication]) 
def log_out(request: Request):
    # pass
    res = {'data': "",  'status': status.HTTP_200_OK}
    try: 
        token = str(request.auth)
        print(f"request.auth 👏{str(request.auth)}")
        t = Token.objects.get(key=token)
        if t: 
            usr = t.user
        else:
            usr = ''
        res['data'] = {"user": str(usr), "message": 'logged out'}
        t.delete()
        res['status'] =  status.HTTP_200_OK
    except Exception as e:
        res['data'] = {"message" : e}
        res['status'] = status.HTTP_400_BAD_REQUEST
    return Response(**res)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request: Request):
    try:
        
        token = str(request.auth)
        t = Token.objects.get(key=token)
        u = t.user
        usr = UserSerializer(t.user)
        return Response(**{'data': usr.data,  'status': status.HTTP_200_OK})
    except Exception as e:
        return Response(**{'data': str(e),  'status': status.HTTP_402_PAYMENT_REQUIRED})

@api_view(['GET'])
@permission_classes([])
def get_user(request: Request, user_id):
    try:
        user_model = User.objects.get(pk=user_id)
        usr = UserSerializer(user_model)
        return Response(**{'data': usr.data,  'status': status.HTTP_200_OK})
    except Exception as e:
        return Response(**{'data': str(e),  'status': status.HTTP_404_NOT_FOUND})

# @swagger_auto_schema(method='PATH', query_serializer=UserSerializer)
@api_view(['PATCH', 'PUT'])
@authentication_classes([TokenAuthentication])
def update_user(request: Request, user_id):
    try:
        user_model = User.objects.get(pk=user_id)
        usr = UserSerializer(instance=user_model,data=request.data)

        if usr.is_valid():
            usr.save()

        return Response(**{'data': usr.data, 'status': status.HTTP_200_OK})
    except Exception as e:
        return Response(**{'data': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})

@api_view(['PATCH', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request: Request):
    try:
        token = str(request.auth)
        t = Token.objects.get(key=token)
        u = t.user
        usr = UserSerializer(u,data=request.data)

        if usr.is_valid():
            usr.save()
            return Response(**{'data': usr.data,  'status': status.HTTP_200_OK})
    except Exception as e:
        return Response(**{'data': str(e),  'status': status.HTTP_404_NOT_FOUND})

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_profile(request: Request):
    try:
        token = str(request.auth)
        t = Token.objects.get(key=token)
        u = t.user
        usrnm = u.username
        u.delete()
        return Response(**{'data': {'message': f'{usrnm} deleted'}, 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
    except Exception as e:
        return Response(**{'data': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request: Request, user_id):
    try:
        u = User.objects.get(pk=user_id)
        usrnm = u.username
        u.delete()
        return Response(**{'data': {'message': f'{usrnm} deleted'}, 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
    except Exception as e:
        return Response(**{'data': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([])
def list_users(request: Request):
    try:
        users = User.objects.all().order_by('username')
        usrlist = [UserSerializer(user).data for user in users] 
        return Response(**{'data': usrlist,  'status': status.HTTP_200_OK})
    except Exception as e:  
        return Response(**{'data': str(e),  'status': status.HTTP_500_INTERNAL_SERVER_ERROR})


from django.db.models import Q
from apps.cards.serializers import PinSerializer
import http.client
from urllib.parse import quote
@api_view(['GET'])
def search_autocomplete(request: Request):
    try:
        print(request.GET)
        query = request.GET['q']
        p = Pin.objects.filter(title__icontains=query)
        # print(p)
        pinlist = [PinSerializer(pin).data for pin in p ]
        u = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query)| Q(last_name__icontains=query) | Q(email__icontains=query) )
        usrlist = [UserSerializer(user).data for user in u] 
        
        try:
            conn = http.client.HTTPSConnection("suggestqueries.google.com")
            payload = ''
            headers = {}
            conn.request("GET", f"/complete/search?client=chrome&q={quote(query)}", payload, headers)
            res = conn.getresponse()
            data = res.read()
            
            googlesuggest = data.decode("utf-8").split("]")[0].split("[")[2].split(",")
        except Exception as e:
            print(e)

        
        return Response(**{'data': { 'users': usrlist[:4], 'pins': pinlist[:4], 'google': googlesuggest},  'status': status.HTTP_200_OK})
    except Exception as e:
        return Response(**{'data': str(e),  'status': status.HTTP_500_INTERNAL_SERVER_ERROR})

    pass


from .serializers import UserProfile , UserBoard , SavedPins , Saved_Pins , BoardSerializer
from apps.cards.models import Board ,  Pin, Save

@api_view(['GET'])
def list_user(request: Request,id):
    users=User.objects.filter(id=id)
    Serialzed_data = UserProfile(instance=users,many=True)
    return Response(data=Serialzed_data.data,status=status.HTTP_200_OK)

@api_view(['GET'])
def list_board(request,id):
    boards = Board.objects.filter(creator=id)
    Serialzed_data = UserBoard(boards,many=True)
    return Response(data=Serialzed_data.data,status=status.HTTP_200_OK)
swagger_auto_schema(method='POST', query_serializer=BoardSerializer)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_board(request: Request):
    if request.method == 'POST':
        data={
            'name':request.data.get('name'),
            'creator':request.user.id,
        }
        new_board = BoardSerializer(data=data)
        if new_board.is_valid():
            new_board.save()
            return Response(new_board.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=new_board.errors)


@api_view(['GET'])
def list_pin(request: Request,id):
    saved_pins = Pin.objects.filter(id=id)
    Serialzed_data = SavedPins(saved_pins,many=True)
    return Response(data=Serialzed_data.data,status=status.HTTP_200_OK)

@api_view(['GET'])
def list_savedpin(request: Request,id):
    saved_pins = User.objects.filter(id=id)
    Serialzed_data = Saved_Pins(saved_pins,many=True)
    return Response(data=Serialzed_data.data,status=status.HTTP_200_OK)

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_reactees(request: Request,id):
    saved_pins = Pin.objects.get(id=id)
    user = User.objects.get(id=request.user.id)
    if request.method == 'PATCH':
        try:
            saved_pins.reactees.add(user)
            return Response(**{'data': 'done', 'status': status.HTTP_200_OK})
        except Exception as e:
            return Response(**{'data': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
    else:
        try:
            saved_pins.reactees.remove(user)
            return Response(**{'data': 'deleted', 'status': status.HTTP_200_OK})
        except Exception as e:
            return Response(**{'data': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def create_pinboard(request: Request):
    pin = Pin.objects.get(id=request.data.get('pin_id'))
    board = Board.objects.get(id=request.data.get('board_id'))
    if request.method == 'PATCH':
        try:
            board.pins.add(pin)
            return Response(**{'data': 'done', 'status': status.HTTP_200_OK})
        except Exception as e:
            return Response(**{'data': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
    else:
        try:
            board.pins.remove(pin)
            return Response(**{'data': 'deleted', 'status': status.HTTP_200_OK})
        except Exception as e:
            return Response(**{'data': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})