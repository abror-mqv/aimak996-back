from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




class CityBoard(models.Model):
    city = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='city_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    playmarket_link = models.URLField(blank=True, null=True)
    appstore_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Доска: {self.city}"
    


class PinnedMessage(models.Model):
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    cities = models.ManyToManyField("ads.City", related_name="pinned_messages")

    def __str__(self):
        return f"PinnedMessage({self.text[:30]}...)"