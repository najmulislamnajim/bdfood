from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem

class CartItemSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization of cart items, including item and quantity.
    """
    class Meta:
        model = CartItem
        fields = ['item', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    """
    Includes nested serialization of CartItem instances.
    """
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['customer', 'items', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization of order items, including item, quantity, and price.
    """
    class Meta:
        model = OrderItem
        fields = ['item', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    """
    Includes nested serialization of OrderItem instances.
    Provides details of an order, including customer, restaurant, total price, status, and items.
    """
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'total_price', 'status', 'created_at', 'items']
