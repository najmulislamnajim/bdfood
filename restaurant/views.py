from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token
from account.models import Restaurant,User
from .serializers import RestaurantSerializer,EmployeeSerializer,EmployeesSerializer,EmployeePermissionSerializer,CategorySerializer,ItemSerializer
from .models import EmployeePermission,Category,Item


class RestaurantView(APIView):
    """
    API view for handling restaurant creation and listing.
    Allows authenticated users to list their own restaurants
    and allows only owners to create new restaurants.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        List all restaurants owned by the authenticated user.
        """
        restaurants = Restaurant.objects.filter(owner=request.user)
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Allow only owners to create a new restaurant.
        Checks if the user is an owner before allowing restaurant creation.
        """
        if request.user.role != 'owner':
            return Response({"error": "Only owners can create restaurants."}, status=status.HTTP_403_FORBIDDEN)

        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class EmployeeView(APIView):
    """
    API view for handling employee  listing.
    Only the restaurant owner can list or manage employees.
    """
    permission_classes = [IsAuthenticated]
    def get(self,request,restaurant_id):
        """
        List all employees for a specific restaurant owned by the authenticated user.
        """
        if request.user.role != 'owner':
            return Response({"error": "Only owners can view their restaurant employees."}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Ensure the restaurant is owned by the authenticated user
            restaurant = Restaurant.objects.get(id=restaurant_id, owner=request.user)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found or not owned by you."}, status=status.HTTP_404_NOT_FOUND)

        # Get all employees associated with the restaurant
        employees = User.objects.filter(restaurant=restaurant, role='employee')
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmployeesView(APIView):
    """
    API view to list restaurants owned by the authenticated user
    and group employees by each restaurant.Only accessible by owners.
    """
    permission_classes=[IsAuthenticated]
    def get(self,request):
        """
        List all restaurants owned by the authenticated user,including employees grouped by each restaurant.
        """
        if request.user.role != 'owner':
            return Response({"error": "Only owners can view their restaurant employees."}, status=status.HTTP_403_FORBIDDEN)

        # Get all restaurants owned by the authenticated user
        restaurants = Restaurant.objects.filter(owner=request.user)

        data = []
        for restaurant in restaurants:
            employees = User.objects.filter(restaurant=restaurant, role='employee')
            restaurant_data = {
                'id': restaurant.id,
                'name': restaurant.name,
                'location': restaurant.location,
                'employees': EmployeeSerializer(employees, many=True).data
            }
            data.append(restaurant_data)

        return Response(data, status=status.HTTP_200_OK)



class EmployeePermissionView(APIView):
    """
    API view for managing employee permissions in a restaurant.
    Only the owner can set or update employee permissions.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Set or update the permissions for an employee.
        Only owners can do this for their own employees.
        """
        employee_email=request.data.get('employee_email')
        restaurant_id=request.data.get('restaurant_id')
        can_create=request.data.get('can_create')
        can_update=request.data.get('can_update')
        can_delete=request.data.get('can_delete')
        try:
            employee = User.objects.get(email=employee_email,restaurant=restaurant_id, role='employee')
            restaurant = employee.restaurant
        except User.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user != restaurant.owner:
            return Response({"error": "You can only set permissions for your own restaurant's employees."}, status=status.HTTP_403_FORBIDDEN)

        permission, created = EmployeePermission.objects.get_or_create(employee=employee, restaurant=restaurant)

        permission.can_create = can_create
        permission.can_update = can_update
        permission.can_delete = can_delete
        permission.save()  

        serializer = EmployeePermissionSerializer(permission)
        return Response({"message": "Permissions updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
    
    
class CategoryView(APIView):
    """
    API view for managing categories within a restaurant.
    The owner or employees with the appropriate permissions can create, update, and delete categories.
    """
    permission_classes = [IsAuthenticated]

    def has_permission(self, user, restaurant, action):
        """
        Helper function to check if the user has permission to perform the action.
        Owners always have full permissions. Employees need explicit permissions.
        """
        if user == restaurant.owner:
            return True  # Owners have all permissions

        # For employees, check the EmployeePermission table
        try:
            permission = EmployeePermission.objects.get(employee=user, restaurant=restaurant)
            if action == 'create' and permission.can_create:
                return True
            if action == 'update' and permission.can_update:
                return True
            if action == 'delete' and permission.can_delete:
                return True
        except EmployeePermission.DoesNotExist:
            return False

        return False

    def post(self, request):
        """
        Create a new category for a restaurant.
        Requires 'create' permission for employees.
        """
        serializer = CategorySerializer(data=request.data)
        restaurant_id = request.data.get('restaurant')

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to create categories
        if not self.has_permission(request.user, restaurant, 'create'):
            return Response({"error": "You do not have permission to create categories."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save(restaurant=restaurant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update an existing category.
        Requires 'update' permission for employees.
        """
        category_id=request.data.get('category_id')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to update categories
        if not self.has_permission(request.user, category.restaurant, 'update'):
            return Response({"error": "You do not have permission to update this category."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Delete an existing category.
        Requires 'delete' permission for employees.
        """
        category_id=request.data.get('category_id')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to delete categories
        if not self.has_permission(request.user, category.restaurant, 'delete'):
            return Response({"error": "You do not have permission to delete this category."}, status=status.HTTP_403_FORBIDDEN)

        category.delete()
        return Response({"message": "Category deleted successfully."}, status=status.HTTP_200_OK)
    
    
class ItemView(APIView):
    """
    API view for managing items within a category.
    The owner or employees with the appropriate permissions can create, update, and delete items.
    """
    permission_classes = [IsAuthenticated]
    
    def has_permission(self, user, restaurant, action):
        """
        Helper function to check if the user has permission to perform the action.
        Owners always have full permissions. Employees need explicit permissions.
        """
        if user == restaurant.owner:
            return True  # Owners have all permissions

        # For employees, check the EmployeePermission table
        try:
            permission = EmployeePermission.objects.get(employee=user, restaurant=restaurant)
            if action == 'create' and permission.can_create:
                return True
            if action == 'update' and permission.can_update:
                return True
            if action == 'delete' and permission.can_delete:
                return True
        except EmployeePermission.DoesNotExist:
            return False

        return False

    def post(self, request):
        """
        Create a new item in a category.
        Requires 'create' permission for employees.
        """
        serializer = ItemSerializer(data=request.data)
        category_id = request.data.get('category')

        try:
            category = Category.objects.get(id=category_id)
            restaurant = category.restaurant
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to create items
        if not self.has_permission(request.user, restaurant, 'create'):
            return Response({"error": "You do not have permission to create items."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save(category=category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update an existing item.
        Requires 'update' permission for employees.
        """
        item_id=request.data.get('item_id')
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to update items
        if not self.has_permission(request.user, item.category.restaurant, 'update'):
            return Response({"error": "You do not have permission to update this item."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Delete an existing item.
        Requires 'delete' permission for employees.
        """
        item_id=request.data.get('item_id')
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to delete items
        if not self.has_permission(request.user, item.category.restaurant, 'delete'):
            return Response({"error": "You do not have permission to delete this item."}, status=status.HTTP_403_FORBIDDEN)

        item.delete()
        return Response({"message": "Item deleted successfully."}, status=status.HTTP_200_OK)
    
class CategoryListView(APIView):
    """
    API view for listing categories for a specific restaurant.
    This endpoint is publicly accessible.
    """
    permission_classes = [AllowAny]
    
    def get(self,request,restaurant_id):
        """
        List all categories for a given restaurant.
        Requires the restaurant ID as a path parameter.
        """
        if not restaurant_id:
            return Response({"error": "Restaurant ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            restaurant=Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found."}, status=status.HTTP_404_NOT_FOUND)
        categories=Category.objects.filter(restaurant=restaurant)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ItemsListview(APIView):
    """
    API view for listing items within a specific category.
    This endpoint is publicly accessible.
    """
    permission_classes = [AllowAny]
    
    def get(self, request,category_id):
        """
        List all items for a specific category.
        Requires the category ID as a path parameter.
        """
        if not category_id:
            return Response({"error": "Category ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        items = Item.objects.filter(category=category)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)