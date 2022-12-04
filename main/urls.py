from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
	path('', views.HomepageView.as_view(), name='homepage'),
	path('search/', views.SearchView.as_view(), name='search_posts')
]
