from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from users.views import register_view, login_view, logout_view, profile_view, profile_update, ChangePasswordView

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile_update/', profile_update, name='profile_update'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
]
