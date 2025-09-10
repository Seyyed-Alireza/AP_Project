from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Main dashboard
    path('', views.cf_dashboard, name='cf_dashboard'),
    
    # Test URL
    path('test/', views.test_view, name='test'),
    
    # UBCF and IBCF views
    path('ubcf/', views.ubcf_recommendations, name='ubcf'),
    path('ibcf/', views.ibcf_recommendations, name='ibcf'),
    
    # Utility views
    path('similarity-matrices/', views.similarity_matrices_view, name='similarity_matrices'),
    
    # API endpoints
    path('api/predict-rating/<int:product_id>/', views.predict_rating_api, name='predict_rating'),
]
