from django.urls import path
from .views import AddToCartView,ViewCartView,RemoveFromCartView,UpdateCartItemView,ConfirmCartView

urlpatterns = [
    path('cart/add/',AddToCartView.as_view()),
    path('cart/remove/',RemoveFromCartView.as_view()),
    path('cart/update/', UpdateCartItemView.as_view()),
    path('cart/', ViewCartView.as_view()),
    path('cart/confirm/', ConfirmCartView.as_view()),  #for order
]
