from django.contrib import admin
from .models import Category, CityBoard, PinnedMessage, Contacts
# Register your models here.
admin.site.register(Category)
admin.site.register(CityBoard)
admin.site.register(PinnedMessage)
admin.site.register(Contacts)