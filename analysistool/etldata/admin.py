from django.contrib import admin

# Register your models here.
from .models import Measurements, Part

admin.site.register(Measurements)
admin.site.register(Part)

