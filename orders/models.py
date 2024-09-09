from django.db import models
from account.models import User
from restaurant.models import Item,Restaurant

class Cart(models.Model):
    """
    Cart model to store items temporarily before placing an order.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.customer.email}"

class CartItem(models.Model):
    """
    CartItem model to represent individual items in the cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item.name} (Quantity: {self.quantity})"

class Order(models.Model):
    """
    Order model to represent an order placed by a customer.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer.email}"

class OrderItem(models.Model):
    """
    OrderItem model to represent individual items in an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} (Order {self.order.id})"
