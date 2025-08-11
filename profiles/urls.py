from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('editprofile/', views.profile_edit, name='editprofile'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.decrease_cart_item, name='decrease_cart_item'),
    path('delete-cart/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('buy_products/', views.buy_products, name='buy_products'),
    path('routine/full/', views.full_routine_view, name='full_routine'),
    path('user-routines', views.routines, name='user_routines'),
    path('routine/hydration/', views.hydration_routine_view, name='hydration_routine'),
    path('routine/mini/', views.mini_routine_view, name='mini_routine'),
]
