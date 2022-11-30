from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.index, name="index"),
    path("product_create/", views.product_create, name='product_create'),
    path("<int:product_pk>/product_detail/", views.product_detail, name='product_detail'),
    path("<int:product_pk>/product_update/", views.product_update, name='product_update'),
    path("<int:product_pk>/product_delete/", views.product_delete, name='product_delete'),
    
]
