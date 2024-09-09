from django.db import models
from account.models import User,Restaurant



class Category(models.Model):
    """
    This model represents a category of items in a restaurant's menu. Each category is linked to a restaurant.
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Item(models.Model):
    """
    This model represents a menu item that belongs to a category in a restaurant's menu.
    Each item has details like name, description, image, and price.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    details = models.TextField(max_length=500)
    image_url=models.CharField(max_length=255,null=True,blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

class EmployeePermission(models.Model):
    """
    This model stores the permissions assigned to an employee for a specific restaurant. 
    Permissions include the ability to create, update, and delete categories or items.
    """
    employee = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    can_create= models.BooleanField(default=False)
    can_update= models.BooleanField(default=False)
    can_delete= models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions for {self.employee.email} at {self.restaurant.name}"
    