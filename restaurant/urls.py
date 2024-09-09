from django.urls import path
from .views import RestaurantView,EmployeeView,EmployeesView,EmployeePermissionView,CategoryView,ItemView,CategoryListView,ItemsListview

urlpatterns = [
    path('list/', RestaurantView.as_view(), name='restaurant_list'),
    path('employees/',EmployeesView.as_view()),
    path('<int:restaurant_id>/employees/',EmployeeView.as_view()),
    path('employee/permission/',EmployeePermissionView.as_view()),
    path('category/',CategoryView.as_view()),
    path('item/', ItemView.as_view()),
    path('<int:restaurant_id>/categories/',CategoryListView.as_view()),
    path('category/<int:category_id>/items/',ItemsListview.as_view()),
]
