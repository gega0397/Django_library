from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from books.forms import BookForm
from users.choices import UserTypeChoices
from users.models import CustomUser
from users.forms import CustomUserCreationForm, LoginForm, CustomUserChangeForm
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy


# Create your views here.

def register_view(request):
    if request.method == 'POST':
        # Create a form that has request.POST
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Set the user's password securely
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                user.set_password(password1)
                user.save()

                messages.success(request, f'Your Account has been created {email} ! Proceed to log in')
                login(request, user)
                return redirect('users:profile')
            else:
                # Handle password mismatch error here
                form.add_error('password2', 'Passwords entered do not match')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                print(user.user_type)
                if user.user_type not in [UserTypeChoices.LIBRARIAN, UserTypeChoices.ADMIN]:
                    return redirect('users:profile')
                else:
                    return redirect('/admin/')
            else:
                form.add_error(field=None, error="Invalid username or password")

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def profile_view(request):
    form = BookForm()
    return render(request, 'users/profile.html', {'form': form})


@login_required
def profile_update(request):
    form = CustomUserChangeForm(instance=request.user)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('users:profile')
    return render(request, 'users/profile_update.html', {'form': form})


class ChangePasswordView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:profile')
    template_name = 'users/change_password.html'
