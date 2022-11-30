from django.db import models
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, Thumbnail
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

# Create your models here.

class Product(models.Model):
    category_choice = ( 
            ("1", "생일"),
            ("2", "가벼운 선물"),
            ("3", "건강/회복"),
            ("4", "스몰럭셔리"),
            ("5", "응원/시험"),
            ("6", "따뜻한 선물"),
            ("7", "쓸모없는 선물"),
            ("8", "결혼/집들이"),
            ("9", "크리스마스"),
            ("10", "명절"),
            ("11", "전자기기"),
        )
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(max_length=2, choices=category_choice)
    price = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_product')

class ProductImages(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    images = ProcessedImageField(upload_to='images/', blank=True, processors=[Thumbnail(400, 300)], format='JPEG', options={'quality':80})

class Review(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField()
    image = ProcessedImageField(upload_to='images/', blank=True, processors=[ResizeToFill(400, 300)], format='JPEG', options={'quality':80})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    like_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_review')

class ReviewComment(models.Model):
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey('Review', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)