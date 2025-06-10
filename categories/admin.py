from django.contrib import admin
from .models import Category, CityBoard, PinnedMessage
# Register your models here.
admin.site.register(Category)
admin.site.register(CityBoard)
admin.site.register(PinnedMessage)