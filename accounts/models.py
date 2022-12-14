from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import Thumbnail
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class User(AbstractUser):
    nickname = models.CharField(max_length=20, unique=False)
    image = ProcessedImageField(
        upload_to="images/",
        null=True,
        blank=True,
        processors=[Thumbnail(400, 400)],
        format="JPEG",
        options={"quality": 80},
    )
    gender = models.BooleanField(default=False)
    birth_date = models.DateField(null=True)
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers"
    )
    blocking = models.ManyToManyField(
        "self", symmetrical=False, related_name="blockers"
    )
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(15)], null=True)

    # user image 없을 시 오류 방지
    @property
    def get_photo_url(self):
        if self.image:
            return self.image.url
        return None
