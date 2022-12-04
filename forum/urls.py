from . import views
from django.urls import path

app_name = 'forum'

urlpatterns = [
    path('post/<int:post_pk>/', views.PostPageView.as_view(), name='post_page'),
    path('post/edit/<int:post_pk>/', views.PostEditView.as_view(), name='post_edit'),
    path('post/delete/<int:post_pk>/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),

    path('post/<int:post_pk>/<str:status>/', views.post_rating_view, name='post_rating'),

    # Comments
    path('comment/<int:comment_pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
]
