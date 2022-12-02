from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model

class SignupForm(UserCreationForm):
    
    class Meta:
        model = get_user_model()
        fields = (
                "nickname",
                "image",
                "gender",
            )

class UpdateForm(UserChangeForm):
    
    class Meta:
        model = get_user_model()
        fields = (
                "image",
            )