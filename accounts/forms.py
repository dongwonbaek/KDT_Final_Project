from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model


class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "nickname",
            "image",
            "gender",
            "birth_date",
        )


class UpdateForm(UserChangeForm):
    password = None  # profile_update에서 password를 없애기 위함. exclude로는 안됨.

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "nickname",
            "gender",
            "image",
        )
