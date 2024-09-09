from django.contrib.auth import login,logout
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import User,OneTimePassword,Restaurant
from .serializers import (OwnerRegistrationSerializer,EmployeeRegistrationSerializer,LoginSerializer,CustomerRegistrationSerializer)
from .utils import send_otp_to_user

# View for owner registration.
class OwnerRegistrationView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        """
        Registers a new owner and sends an OTP for email verification.
        """
        serializer = OwnerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user=serializer.data
            send_otp_to_user(user["email"])
            return Response({"message":"User resgisterd successfully.","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# View for verify owner email using otp. 
class VerifyOwnerEmailView(GenericAPIView):
    permission_classes=[AllowAny]
    def post(self,request):
        """
        Verifies the owner's email using the OTP.
        """
        otp=request.data.get('otp')
        try:
            user_obj=OneTimePassword.objects.get(code=otp)
            user=user_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.is_active=True
                user.save()
                return Response({'message':f'{user.email} is verified'},status=status.HTTP_200_OK)
            return Response({'message':f'{user.email} is already verified'},status=status.HTTP_400_BAD_REQUEST)
        except OneTimePassword.DoesNotExist:
            return Response({'message':f'Invalid OTP'},status=status.HTTP_400_BAD_REQUEST)
      
# View for Employee Registration.  
class EmployeeRegistrationView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        """
        Registers a new employee. The employee remains inactive until verified by the owner.
        """
        serializer=EmployeeRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Employee resgisterd successfully.","note":"wait for owner verify"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for Employee Verification.
class VerifyEmployee(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        """
        Verifies an employee and associates them with the owner's restaurant.
        """
        employee_email=request.data.get('employee_email')
        restaurant_id=request.data.get('restaurant_id')
        if not restaurant_id:
            return Response({"error": "restaurant_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ensure the owner owns the restaurant with the provided restaurant_id
            restaurant = Restaurant.objects.get(id=restaurant_id, owner=request.user)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found or you do not own this restaurant."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            if request.user.role != 'owner':
                return Response({"error": "Only the restaurant owner can verify employees."}, status=status.HTTP_403_FORBIDDEN)
            employee=User.objects.get(email=employee_email,restaurant=restaurant)
        except User.DoesNotExist:
            return Response({"message":"Employee not found or not associated with your restaurant."}, status=status.HTTP_404_NOT_FOUND)
        employee.is_active = True
        employee.is_verified=True
        employee.save()
        return Response({"message": "Employee verified."}, status=status.HTTP_200_OK)
    
    
# View for user login.
class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        """
        Logs in the user and generates an authentication token.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)  # Log the user in
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "phone": user.phone
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for user logout.
class LogoutView(APIView):
    """
    API view for logging out users. It deletes their auth token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logs out the user by deleting their authentication token.
        """
        request.user.auth_token.delete()  # Delete the auth token to log out the user
        logout(request)  # Django's logout function to ensure the session is cleared
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    
# View for customer registration.  
class CutomerRegistrationView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        """
        Registers a customer. The customer is verified and activated by default. We can use otp verification also.
        """
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            user.is_verified=True
            user.is_active=True
            user.save()
            return Response({"message":"User resgisterd successfully.","data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)