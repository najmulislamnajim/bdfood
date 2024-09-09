from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Cart, CartItem,Order,OrderItem
from .serializers import CartSerializer, CartItemSerializer,OrderSerializer,OrderItemSerializer
from restaurant.models import Item

# View for Add to Cart 
class AddToCartView(APIView):
    """
    API to add an item to the cart.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the cart for the current customer
        cart, created = Cart.objects.get_or_create(customer=request.user)

        # Add or update the item in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({"message": "Item added to cart."}, status=status.HTTP_201_CREATED)
    
# View for showing the cart.
class ViewCartView(APIView):
    """
    API to view the cart and its items.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(customer=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

# View for remove items from cart.
class RemoveFromCartView(APIView):
    """
    API to remove an item from the cart.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        item_id = request.data.get('item_id')

        try:
            cart = Cart.objects.get(customer=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, item_id=item_id)
            cart_item.delete()
            return Response({"message": "Item removed from cart."}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

# View for updating the quantity of an item in cart.     
class UpdateCartItemView(APIView):
    """
    API to update the quantity of an item in the cart (increase or decrease).
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        Update the quantity of a cart item.
        """
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        # Check item and quantity passes or not.
        if not item_id or not quantity:
            return Response({"error": "Item ID and quantity are required."}, status=status.HTTP_400_BAD_REQUEST)
        # Check cart exists or not for the authenticated user.
        try:
            cart = Cart.objects.get(customer=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        # Check the item exists in the cart.
        try:
            cart_item = CartItem.objects.get(cart=cart, item_id=item_id)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

        # ensure the quantity not negative or zero)
        if quantity <= 0:
            cart_item.delete()  # If quantity is 0 or less, remove the item from the cart
            return Response({"message": "Item removed from cart due to zero or negative quantity."}, status=status.HTTP_200_OK)
        
        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Cart item quantity updated.", "item": {"id": cart_item.item.id, "quantity": cart_item.quantity}}, status=status.HTTP_200_OK)
    
# View for checkout the cart and creating an order.
class ConfirmCartView(APIView):
    """
    API to confirm the cart and create an order.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(customer=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        
        items = cart.items.all()
        if not items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.quantity * item.item.price for item in items)
        order = Order.objects.create(customer=request.user, restaurant=items.first().item.category.restaurant, total_price=total_price)

        # Add items to the order
        for item in items:
            OrderItem.objects.create(order=order, item=item.item, quantity=item.quantity, price=item.item.price)
        
        # Clear the cart after order placement
        cart.items.all().delete()
        
        serializer = OrderSerializer(order)
        return Response({"message": "Order placed successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
