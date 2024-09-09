from django.contrib import admin
from .models import Category,Item,EmployeePermission

# Register your models here.
admin.site.register(Category)
admin.site.register(EmployeePermission)
admin.site.register(Item)
