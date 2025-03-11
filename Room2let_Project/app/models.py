from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from django.conf import settings

# Create your models here.


class Property(models.Model):
    PURPOSE_CHOICE = (
        ('sell/rent', 'Sell/Rent'),
        ('rent', 'Rent'),
        ('sell', 'Sell'),
    )
    SECURITY_CHOICES = (
        ('guranteed', 'Guranteed'),
        ('not guranteed', 'Not Guranteed'),
    )
    WATER_AVAIL_CHOICES = (
        ('not Available', 'Not Available'),
        ('well', 'Well'),
        ('well with pumping machine', 'Well with pumping machine'),
        ('borehole', 'Borehole'),
    )
    TOILET_CHOICES = (
        ('water closet', 'Water Closet'),
        ('modern Pit', 'Modern Pit'),
        ('pit Latrine', 'Pit Latrine'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    Title = models.CharField(max_length=100)
    Type = models.CharField(max_length=100)
    Price = models.FloatField()
    Purpose = models.CharField(max_length=100, choices=PURPOSE_CHOICE, default='sell/rent')
    Bedrooms = models.IntegerField()
    Bathrooms = models.IntegerField()
    images = models.CharField(max_length=255)
    Address = models.TextField()
    State = models.CharField(max_length=100)
    Local_Govt = models.CharField(max_length=100)
    Area_located_or_close_to = models.CharField(max_length=255)
    Detail_info = models.TextField()
    Compound_security = models.CharField(max_length=100, choices=SECURITY_CHOICES, default='guranteed')
    Water = models.CharField(max_length=100, choices=WATER_AVAIL_CHOICES, default='well')
    Toilets = models.CharField(max_length=100, choices=TOILET_CHOICES, default='water closet')
    Contact_phone_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Title

class UserProfile(AbstractUser):
    phone_number = models.CharField(max_length=100)
    address = models.TextField()
    about = models.TextField(default="", blank=True, null=True)
    Property_count = models.IntegerField(default=0)
    profile_picture = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
class Features(models.Model):
    Property = models.ForeignKey(Property, on_delete=CASCADE)
    name = models.CharField(max_length=100)
    


