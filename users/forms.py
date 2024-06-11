from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import CustomUser
from users.validators import validate_personal_number
from users.choices import UserTypeChoicesForm, UserTypeChoices


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    personal_number = forms.CharField(max_length=11, validators=[validate_personal_number])
    birth_date = forms.DateField()
    # user_type = forms.ChoiceField(choices=UserTypeChoicesForm.choices,)

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password-input'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    # Add a field for password strength
    password_strength = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ("email", 'first_name', 'last_name', 'birth_date', 'personal_number')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.user_type = UserTypeChoices.STUDENT
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    personal_number = forms.IntegerField(validators=[validate_personal_number])
    user_type = forms.ChoiceField(choices=UserTypeChoicesForm.choices,
                                  widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ("email", 'first_name', 'last_name', 'birth_date', 'personal_number', 'user_type')
        exclude = ('password',)

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        # Remove the password field
        # if 'password' in self.fields:
        #     self.fields.pop('password')

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

class LoginForm(forms.Form):
    email = forms.CharField(
        label='Email',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password-input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class CustomUserCreationFormAdmin(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    personal_number = forms.CharField(max_length=11, validators=[validate_personal_number])
    birth_date = forms.DateField()
    user_type = forms.ChoiceField(choices=UserTypeChoices.choices,)

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password-input'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    # Add a field for password strength
    password_strength = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ("email", 'first_name', 'last_name', 'birth_date', 'personal_number', 'user_type')


class CustomUserChangeFormAdmin(UserChangeForm):
    personal_number = forms.IntegerField(validators=[validate_personal_number])
    user_type = forms.ChoiceField(choices=UserTypeChoices.choices,
                                  widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ("email", 'first_name', 'last_name', 'birth_date', 'personal_number', 'user_type')
        exclude = ('password',)

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeFormAdmin, self).__init__(*args, **kwargs)
        # Remove the password field
        # if 'password' in self.fields:
        #     self.fields.pop('password')