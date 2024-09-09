from django.urls import path
from .views import OwnerRegistrationView,VerifyOwnerEmailView,LoginView,LogoutView,EmployeeRegistrationView,VerifyEmployee,CutomerRegistrationView

urlpatterns = [
    path('owner/register/',OwnerRegistrationView.as_view()),
    path('owner/verify/',VerifyOwnerEmailView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('employee/register/',EmployeeRegistrationView.as_view()),
    path('employee/verify/',VerifyEmployee.as_view()),
    path('customer/register/',CutomerRegistrationView. as_view()),    
]
