from django.urls import path
from .views import profile_view, profile_edit, add_to_cart

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('editprofile/', profile_edit, name='editprofile'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'), 
]
