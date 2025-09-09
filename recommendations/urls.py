from django.urls import path
from . import views, cf_views

app_name = 'recommendations'

urlpatterns = [
    # Main recommendation views
    path('', views.get_user_recommendations, name='user_recommendations'),
    path('dashboard/', views.recommendations_dashboard, name='dashboard'),
    path('similar/<int:product_id>/', views.get_similar_products, name='similar_products'),
    
    # Collaborative Filtering views
    path('ubcf/', cf_views.get_ubcf_recommendations, name='ubcf_recommendations'),
    path('ibcf/', cf_views.get_ibcf_recommendations, name='ibcf_recommendations'),
    path('cf-dashboard/', cf_views.cf_dashboard, name='cf_dashboard'),
    path('predict-rating/<int:product_id>/', cf_views.predict_rating, name='predict_rating'),
    path('similarity-matrices/', cf_views.similarity_matrices_view, name='similarity_matrices'),
    
    # API endpoints
    path('api/recommendations/', views.get_user_recommendations, name='api_recommendations'),
    path('api/similar/<int:product_id>/', views.get_similar_products, name='api_similar_products'),
    path('api/record-interaction/', views.record_interaction, name='record_interaction'),
    path('api/ubcf/', cf_views.get_ubcf_recommendations, name='api_ubcf'),
    path('api/ibcf/', cf_views.get_ibcf_recommendations, name='api_ibcf'),
    path('api/predict-rating/<int:product_id>/', cf_views.predict_rating, name='api_predict_rating'),
    
    # Analytics
    path('analytics/', views.RecommendationAnalytics.as_view(), name='analytics'),
]
