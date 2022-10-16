from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.AuthenticationView.as_view(), name='login'),
    path('email/<str:status>/', views.ConfirmEmailView.as_view(), name='email_confirm'),
    path('profile/settings/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),

    # Password reset
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset_password_sent/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Password change
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Change email
    path('email_change/verification/', views.ChangeEmailView.as_view(), name='email_change_verification'),
    path('email_change/confirm/', views.ChangeEmailConfirmView.as_view(), name='email_change_confirm'),
    path('email_change/new_email/<str:status>/', views.ConfirmNewEmailView.as_view(),
         name='email_change_confirm_new_email'),
]
