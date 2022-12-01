from django import forms
from django.forms import ClearableFileInput
from .models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("title", "content", "category", "price")


class ProductImagesForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ("images",)
        widgets = {
            "image": ClearableFileInput(attrs={"multiple": True}),
        }
        labels = {
            "image": "이미지 업로드",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("title", "content", "image", "rating")


class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ("content",)