from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'mainpage'

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('api/mainpage/', views.MainpageAPIView.as_view(), name='api-mainpage'),
    path("api/products/<int:id>/", views.ProductDetailAPI.as_view(), name="product_detail"),
    path("api/like/<int:pk>/", views.ProductLikeAPIView.as_view(), name="product_like"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('more-products/', views.more_products, name='more_products'),
    path('live-search/', views.live_search, name='live_search'),
    path('like/<int:product_id>/', views.like_product, name='like_product'),
]