from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.index, name="index"),
    path("product_create/", views.product_create, name='product_create'),
    path("<int:product_pk>/product_detail/", views.product_detail, name='product_detail'),
    path("<int:product_pk>/product_update/", views.product_update, name='product_update'),
    path("<int:product_pk>/product_delete/", views.product_delete, name='product_delete'),
    path("review_index/", views.review_index, name='review_index'),
    path("<int:product_pk>/review_create/", views.review_create, name='review_create'),
    path("<int:review_pk>/review_update/", views.review_update, name='review_update'),
    path("<int:product_pk>/review_delete/<int:review_pk>/", views.review_delete, name='review_delete'),
    path("<int:review_pk>/review_like/", views.review_like, name='review_like'),
    path("<int:review_pk>/review_comment_create/", views.review_comment_create, name='review_comment_create'),
    path("<int:comment_pk>/review_comment_delete/", views.review_comment_delete, name='review_comment_delete'),

]
