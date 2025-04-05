from django.contrib import admin
from .models import Property, UserProfile, Features, Interest

# Register your models here.

admin.site.register(Property)
admin.site.register(UserProfile)
admin.site.register(Features)
admin.site.register(Interest)
# Compare this snippet from Room2let_Project/app/views.py:

