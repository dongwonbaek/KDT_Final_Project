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
            "images": ClearableFileInput(attrs={"multiple": True}),
        }
        labels = {
            "images": "이미지 업로드",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("title", "content", "image", "rating")
        labels = {
            "title": '제목',
            "content": '내용',
            "image": '이미지',
            "rating": '평점',
        }


class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ("content",)


class CommunityForm(forms.ModelForm):
    
    class Meta:
        model = Community
        fields = ("title", "content")


class CommunityImagesForm(forms.ModelForm):
    class Meta:
        model = CommunityImages
        fields = ("images",)
        widgets = {
            "images": ClearableFileInput(attrs={"multiple": True}),
        }
        labels = {
            "images": "이미지 업로드",
        }
