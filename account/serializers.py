from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, Restaurant

class BaseRegistrationSerializer(serializers.ModelSerializer):
    """
    Base serializer to handle common fields and validation
    for user registration (Owner, Employee, Customer).
    """
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        """
        Validate that the two password fields match.
        """
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create_user(self, validated_data, role, restaurant=None):
        """
        Helper method to create a user with a specific role and
        optional restaurant assignment.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            role=role,
            password=validated_data['password'],
            restaurant=restaurant,
        )
        user.save()
        return user

class OwnerRegistrationSerializer(BaseRegistrationSerializer):
    """
    Serializer for registering an owner. Inherits common
    validation from BaseRegistrationSerializer.
    """
    def create(self, validated_data):
        """
        Creates an Owner user.
        """
        return self.create_user(validated_data, role='owner')

class EmployeeRegistrationSerializer(BaseRegistrationSerializer):
    """
    Serializer for registering an employee. Requires a restaurant ID.
    """
    restaurant_id = serializers.CharField(write_only=True)

    class Meta(BaseRegistrationSerializer.Meta):
        fields = BaseRegistrationSerializer.Meta.fields + ['restaurant_id']

    def create(self, validated_data):
        """
        Creates an Employee user and associates them with a restaurant.
        """
        restaurant = Restaurant.objects.get(id=validated_data['restaurant_id'])
        return self.create_user(validated_data, role='employee', restaurant=restaurant)

class CustomerRegistrationSerializer(BaseRegistrationSerializer):
    """
    Serializer for registering a customer. Inherits common
    validation from BaseRegistrationSerializer.
    """
    def create(self, validated_data):
        """
        Creates a Customer user.
        """
        return self.create_user(validated_data, role='customer')

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Validates email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Authenticate the user with provided credentials.
        """
        user = authenticate(email=data['email'], password=data['password'])
        if user:
            if not user.is_active:
                raise serializers.ValidationError("This account is inactive.")
            return user
        raise serializers.ValidationError("Invalid login credentials.")
