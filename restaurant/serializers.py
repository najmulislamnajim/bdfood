from account.models import User,Restaurant
from rest_framework import serializers 
from .models import EmployeePermission,Category,Item

class RestaurantSerializer (serializers.ModelSerializer):
    """
    Handles the serialization of restaurant objects, allowing the owner to be linked to a restaurant.
    """
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Restaurant
        fields=["id","name","location","owner"]
        
class EmployeeSerializer (serializers.ModelSerializer):
    """
    Serializes employee-related fields, including email, first name, last name, phone, and verification status.
    """
    class Meta:
        model=User
        fields=["email","first_name","last_name","phone","is_verified"]

class EmployeesSerializer(serializers.ModelSerializer):
    """
    This serializer groups employees based on the restaurant they are linked to.
    It uses the EmployeeSerializer to list all employees associated with a restaurant.
    """
    employees = EmployeeSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'employees']
        
class EmployeePermissionSerializer(serializers.ModelSerializer):
    """
    Serializes the permissions granted to an employee, including whether they can create, update, or delete items or categories.
    """
    class Meta:
        model = EmployeePermission
        fields=['employee','restaurant','can_create','can_update','can_delete',]
        
class CategorySerializer(serializers.ModelSerializer):
    """
    Handles serialization for categories within a restaurant's menu. Each category is linked to a restaurant.
    """
    class Meta:
        model = Category
        fields=['id', 'name','restaurant']

class ItemSerializer(serializers.ModelSerializer):
    """
    Serializes items belonging to a category, including details like name, description, image URL, price, and the category it belongs to.
    """
    class Meta:
        model = Item
        fields=['id', 'name','details','image_url','price','category']
    