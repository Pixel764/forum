from . import views
from django.urls import path, re_path

app_name = 'forum'

urlpatterns = [
    path('post/<int:post_pk>/', views.PostPageView.as_view(), name='post_page'),
    path('post/edit/<int:post_pk>/', views.PostEditView.as_view(), name='post_edit'),
    path('post/delete/<int:post_pk>/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('', views.HomepageView.as_view(), name='homepage'),
]
