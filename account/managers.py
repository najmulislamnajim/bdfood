from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

"""
Override UserManager to create user and super for our custom user model.
"""
class UserManager(BaseUserManager):
    """
    Check email is valid or not.
    """
    def email_validator(self,email):
        try:
            validate_email(email)
        except :
            raise ValidationError("Invalid email address")
        
    """
    Override create_user method.
    """
    def create_user(self, email,first_name,last_name,phone, password, **extra_fields):
        # ensure that all data are passed.
        if email:
            email=self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValidationError("Email must be provided")
        if not first_name:
            raise ValidationError("first_name is required")
        if not last_name:
            raise ValidationError("last_name is required")
        if not phone:
            raise ValidationError("phone is required")
        # create user
        user = self.model(email=email,first_name=first_name,last_name=last_name,phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    """
    Override create_super_user method.
    """
    def create_superuser(self,email,first_name,last_name,phone,password,**extra_fields):
        # set default value for is_staff, is_superuser, is_verified, is_active
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        extra_fields.setdefault("is_verified",True)
        extra_fields.setdefault("is_active",True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("is_staff must be true for admin user")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("is_superuser must be true for admin user")

        if extra_fields.get("is_active") is not True:
            raise ValueError("is_active must be true for admin user")
        
        user =self.create_user(email,first_name,last_name,phone,password,**extra_fields)
        user.save(using=self._db)
        return user