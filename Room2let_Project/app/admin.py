from django.contrib import admin
from .models import Property, UserProfile, Features

# Register your models here.

admin.site.register(Property)
admin.site.register(UserProfile)
admin.site.register(Features)
# Compare this snippet from Room2let_Project/app/views.py:

