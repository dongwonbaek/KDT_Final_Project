from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('update/', views.update, name='update'),
    path('delete/', views.delete, name='delete'),
    path('password/', views.password, name='password'),
    path('<int:user_pk>/detail/', views.detail, name='detail'),
    path('<int:user_pk>/follow/', views.follow, name='follow'),
    path('<int:user_pk>/block/', views.block, name='block'),
]