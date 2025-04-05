from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from .managers import UserProfileManager
from django.contrib.auth import get_user_model

# Create your models here.

class UserProfile(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('agent', 'Agent'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, default='name')
    username = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100)
    address = models.TextField()
    role = models.CharField(max_length=100, choices=ROLES, default='user')
    about = models.TextField(default="", blank=True, null=True)
    property_count = models.IntegerField(default=0)
    profile_picture = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_token_expiry = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'role']

    objects = UserProfileManager()


    
    def __str__(self):
        return f"{self.email} - {self.role}"
    

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
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(UserProfile, on_delete=CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='pending')
    title = models.CharField(max_length=100)
    property_type = models.CharField(max_length=100)
    price = models.FloatField()
    purpose = models.CharField(max_length=100, choices=PURPOSE_CHOICE, default='sell/rent')
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    images = models.CharField(max_length=255)
    address = models.TextField()
    state = models.CharField(max_length=100)
    local_Govt = models.CharField(max_length=100)
    area_located_or_close_to = models.CharField(max_length=255)
    detail_info = models.TextField()
    compound_security = models.CharField(max_length=100, choices=SECURITY_CHOICES, default='guranteed')
    water = models.CharField(max_length=100, choices=WATER_AVAIL_CHOICES, default='well')
    toilets = models.CharField(max_length=100, choices=TOILET_CHOICES, default='water closet')
    contact_phone_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.email} - {self.status}"

class Features(models.Model):
    property = models.ManyToManyField(Property)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Interest(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    state = models.CharField(max_length=100)
    local_Govt = models.CharField(max_length=100)
    search_query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.state} - {self.local_Govt}"


