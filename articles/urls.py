from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.index, name="index"),
    path("product_list/<category_pk>/", views.product_list, name='product_list'),
    path("product_create/", views.product_create, name='product_create'),
    path("<int:product_pk>/product_detail/", views.product_detail, name='product_detail'),
    path("<int:product_pk>/product_update/", views.product_update, name='product_update'),
    path("<int:product_pk>/product_delete/", views.product_delete, name='product_delete'),
    path("review_index/", views.review_index, name='review_index'),
    path('<int:product_pk>/like/', views.like, name='like'),
    path("<int:product_pk>/review_create/", views.review_create, name='review_create'),
    path("<int:review_pk>/review_update/", views.review_update, name='review_update'),
    path("<int:product_pk>/review_delete/<int:review_pk>/", views.review_delete, name='review_delete'),
    path("<int:review_pk>/review_comment_create/", views.review_comment_create, name='review_comment_create'),
    path("<int:comment_pk>/review_comment_delete/", views.review_comment_delete, name='review_comment_delete'),
    path('product_rank/', views.product_rank, name='product_rank'),
    path('product_rank_redirect/', views.product_rank_redirect, name='product_rank_redirect'),
    path('search/', views.search, name='search'),
    path("<int:review_pk>/review_good/", views.review_good, name='review_good'),
    path("<int:review_pk>/review_cool/", views.review_cool, name='review_cool'),
    path("<int:review_pk>/review_fun/", views.review_fun, name='review_fun'),
    path("<int:review_pk>/review_sad/", views.review_sad, name='review_sad'),
    path("community_index/", views.community_index, name='community_index'),
    path("community_create/", views.community_create, name='community_create'),
    path("<int:community_pk>/community_update/", views.community_update, name='community_update'),
    path("<int:community_pk>/community_delete/", views.community_delete, name='community_delete'),
    path("<int:community_pk>/community_detail/", views.community_detail, name='community_detail'),
    # path("<int:community_pk>/community_comment_create/", views.community_comment_create, name='community_comment_create'),
]
