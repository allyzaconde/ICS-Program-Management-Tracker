from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    firstname = forms.CharField(required=True, label='First Name')
    lastname = forms.CharField(required=True, label='Last Name')

    class Meta:
        model = User
        fields = ["username", "email", "firstname", "lastname", "password1", "password2"]