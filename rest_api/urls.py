from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('posts/', views.PostAPI.as_view({'get': 'list'}), name='posts_all'),
    path(
        'post/<int:pk>/', views.PostAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='post_get_edit_delete'
    ),
    path('post/create/', views.PostAPI.as_view({'post': 'create'}), name='post_create'),
    path('post/<int:pk>/comments', views.CommentAPI.as_view({'get': 'list'}), name='post_comments'),
    path('post/<int:pk>/<str:status>/', views.PostRatingAPI.as_view(), name='post_rating'),

    path(
        'comment/<int:pk>/', views.CommentAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='comment_get_edit_delete'
    ),
    path('comment/<int:pk>/<str:status>/', views.CommentRatingAPI.as_view(), name='comment_rating'),
    path('comment/create/', views.CommentAPI.as_view({'post': 'create'}), name='comment_create'),

    path('categories/', views.CategoryAPI.as_view({'get': 'list'}), name='categories_list'),
    path('category/<int:pk>/', views.CategoryAPI.as_view({'get': 'retrieve'}), name='category_posts'),

    path('user/<str:username>/posts/', views.UserPostsAPI.as_view(), name='user_posts'),
]
