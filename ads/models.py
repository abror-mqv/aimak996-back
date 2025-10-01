from datetime import timedelta, timezone
from django.db import models
from categories.models import Category
from users.models import User



class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    moderator_phone = models.CharField(max_length=20, blank=True, null=True)

    text_for_share = models.TextField(max_length=1000, blank=True, null=True, default="")

    def __str__(self):
        return self.name

class Ad(models.Model):
    description = models.TextField()
    contact_phone = models.CharField(max_length=20)
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE, related_name='ads')
    cities = models.ManyToManyField('City', related_name='ads')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ads', null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.contact_phone} - {self.category.name_kg}"

    def is_expired(self):
        if self.category.name.lower() == "попутка":
            lifetime = timedelta(days=5)
        else:
            lifetime = timedelta(days=30)

        return timezone.now() > self.created_at + lifetime


class AdPhoto(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='ad_photos/')

    def delete(self, *args, **kwargs):
        storage, path = self.image.storage, self.image.path
        super().delete(*args, **kwargs)
        if storage.exists(path):
            storage.delete(path)