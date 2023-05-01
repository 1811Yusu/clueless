from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path
from apps.user import views
from .views import list_user , list_board , list_pin , list_savedpin , update_reactees, create_board,create_pinboard

app_name="apps=user"
urlpatterns = [
    path('get-token/', obtain_auth_token), 
    path('example/', views.example_view), 
    path('signup/', views.sign_up), 

    path('login/', obtain_auth_token, name='login'),
    path('logout/', views.log_out, name="logout" ), 
    path('profile/', views.profile, name='profile'), 
    path('profile/delete/', views.delete_profile, name='delete_profile'), 
    path('profile/update/', views.update_profile, name='update_profile'),

    path('users/', views.list_users), 
    path('users/create/', views.sign_up), 
    path('users/<int:user_id>/', views.get_user, name="get_user"),
    path('users/<int:user_id>/delete/', views.delete_user, name="delete_user"),
    path('users/<int:user_id>/update/', views.update_user, name="update_user"),
    
    path('suggestquery/', views.search_autocomplete),
    

    path('list/<int:id>/',list_user,name='get-data'),
    path('board/<int:id>/',list_board,name='get-board'),
    path('pin/<int:id>/',list_pin,name='get-pin'),
    path('save/<int:id>/',list_savedpin,name='get-savedpin'),
    path('pin/update/<int:id>/', update_reactees, name='update-pin'),
    path('board/create/',create_board , name='update-pin'),
    path('board/pin/create/',create_pinboard , name='update-boardpin'),
]