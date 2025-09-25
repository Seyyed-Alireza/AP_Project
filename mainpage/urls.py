from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'mainpage'

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('api/mainpage/', views.MainpageAPIView.as_view(), name='api-mainpage'),
    path("api/products/<int:id>/", views.ProductDetailAPI.as_view(), name="product_detail"),
    # path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('more-products/', views.more_products, name='more_products'),
    path('live-search/', views.live_search, name='live_search'),
    path('like/<int:product_id>/', views.like_product, name='like_product'),
]