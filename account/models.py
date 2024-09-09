import random
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
from .constants import ROLES

# Create your models here.
class Restaurant(models.Model):
    """
    This model represents a restaurant, which includes basic details like name, location,and a foreign key to the owner (who is a user with an 'owner' role).
    """
    name = models.CharField(max_length=100)
    location=models.CharField(max_length=255)
    owner=models.ForeignKey("User",on_delete=models.CASCADE,related_name='restaurants')

    def __str__(self):
        return self.name


class User(AbstractBaseUser,PermissionsMixin):
    """
    This model extends Django's AbstractBaseUser and PermissionsMixin to create a custom user model. 
    It uses email as the primary identifier and supports role-based access control. 
    Users can be linked to restaurants (for employees or owners) and have fields like phone, role, etc.
    official documentation for custom user model: https://docs.djangoproject.com/en/5.1/topics/auth/customizing/
    """
    email=models.CharField(max_length=255,unique=True,primary_key=True,verbose_name=_("Email Address"))
    first_name=models.CharField(max_length=50,verbose_name="First Name")
    last_name=models.CharField(max_length=50,verbose_name="Last Name")
    phone=models.CharField(max_length=20,verbose_name="Phone Number")
    role=models.CharField(max_length=30, choices=ROLES,verbose_name="Role")
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE, null=True, blank=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['first_name','last_name','phone']
    objects=UserManager()
    
    def __str__(self) -> str:
        return f'{self.email}'
    
    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
   
class OneTimePassword(models.Model):
    """
    This model is used for storing a one-time password (OTP) associated with a user. 
    It's used for verifying a user's email during registration.
    """
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    code=models.CharField(max_length=6,unique=True)
    
    def __str__(self):
        return f'{self.user.first_name}-passcode'
    

