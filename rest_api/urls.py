from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
	path('posts/', views.PostCRUDAPI.as_view({'get': 'list'}), name='all_posts'),
	path('posts/<int:amount>/', views.PostCRUDAPI.as_view({'get': 'list'}), name='amount_posts'),
	path(
		'post/<int:pk>/', views.PostCRUDAPI.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
		name='get_edit_delete_post'
	),
	path('post/create/', views.PostCRUDAPI.as_view({'post': 'create'}), name='create_post'),
	path('post/<int:pk>/<str:status>/', views.PostRatingAPI.as_view(), name='post_rating'),

	path('categories/', views.CategoryAPI.as_view({'get': 'list'}), name='categories_list'),
	path('category/<int:pk>/', views.CategoryAPI.as_view({'get': 'retrieve'}), name='category_posts'),

	path('user/<str:username>/posts/', views.UserPostsAPI.as_view(), name='user_posts'),
	path('user/<str:username>/posts/<int:amount>/', views.UserPostsAPI.as_view(), name='user_amount_posts'),
]
