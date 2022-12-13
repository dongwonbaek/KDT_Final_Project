from bootstrap_datepicker_plus.widgets import (
    DatePickerInput,
    MonthPickerInput,
    YearPickerInput,
)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model


GENDER_CHOICE = [
    "여성",
    "남성",
]


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
        )
        gender = forms.BooleanField(
            label="성별", widget=forms.RadioSelect(choices=GENDER_CHOICE)
        )

        widgets = {
            "birth_date": DatePickerInput(),
        }


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
