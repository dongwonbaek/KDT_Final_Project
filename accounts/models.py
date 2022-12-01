from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import Thumbnail

# Create your models here.


class User(AbstractUser):
    image = ProcessedImageField(
        upload_to="images/",
        blank=True,
        processors=[Thumbnail(400, 400)],
        format="JPEG",
        options={"quality": 80},
    )
    gender = models.BooleanField(default=False)
    birth_date = models.DateField(null=False)
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers"
    )
    blocking = models.ManyToManyField(
        "self", symmetrical=False, related_name="blockers"
    )

    # user image 없을 시 오류 방지
    @property
    def get_photo_url(self):
        if self.image:
            return self.image.url
        return None
