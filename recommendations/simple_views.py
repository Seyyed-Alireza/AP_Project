from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from mainpage.models import Product
from .engine import RecommendationEngine
import json
import pandas as pd


@login_required
def ubcf_recommendations(request):
    """
    User-Based Collaborative Filtering recommendations view
    """
    user_id = request.user.id
    n_recommendations = int(request.GET.get('count', 10))
    
    engine = RecommendationEngine()
    
    try:
        # Get UBCF recommendations with reasons
        recommendations_with_reasons = engine.user_based_collaborative_filtering(
            user_id, n_recommendations, include_reasons=True
        )
        
        # Get recommended products
        recommended_ids = [pid for pid, reason in recommendations_with_reasons]
        products = Product.objects.filter(id__in=recommended_ids)
        
        # Create recommendation objects with additional info
        recommendations = []
        for product in products:
            # Find the reason for this product
            reason = next((reason for pid, reason in recommendations_with_reasons if pid == product.id), "")
            
            # Get predicted rating
            predicted_rating = engine.predict_rating(user_id, product.id, method='ubcf')
            
            recommendations.append({
                'product': product,
                'reason': reason,
                'predicted_rating': predicted_rating
            })
        
        # Get user similarity matrix (limited for display)
        user_similarity_matrix = engine.calculate_user_similarity()
        if user_similarity_matrix is not None:
            # Limit to first 10 users for display
            limited_matrix = user_similarity_matrix.iloc[:10, :10]
        else:
            limited_matrix = None
        
        # Calculate stats
        total_users = User.objects.count()
        total_products = Product.objects.count()
        avg_similarity = user_similarity_matrix.values.mean() if user_similarity_matrix is not None else 0
        coverage = (len(recommendations) / n_recommendations * 100) if n_recommendations > 0 else 0
        
        context = {
            'recommendations': recommendations,
            'user_similarity_matrix': limited_matrix,
            'total_users': total_users,
            'total_products': total_products,
            'avg_similarity': avg_similarity,
            'coverage': coverage,
            'method': 'UBCF',
        }
        
        return render(request, 'recommendations/ubcf.html', context)
        
    except Exception as e:
        print(f"Error in UBCF recommendations: {str(e)}")
        return render(request, 'recommendations/ubcf.html', {
            'error': 'خطا در تولید توصیه‌ها',
            'total_users': User.objects.count(),
            'total_products': Product.objects.count(),
        })


@login_required
def ibcf_recommendations(request):
    """
    Item-Based Collaborative Filtering recommendations view
    """
    user_id = request.user.id
    n_recommendations = int(request.GET.get('count', 10))
    
    engine = RecommendationEngine()
    
    try:
        # Get IBCF recommendations with reasons
        recommendations_with_reasons = engine.item_based_collaborative_filtering(
            user_id, n_recommendations, include_reasons=True
        )
        
        # Get recommended products
        recommended_ids = [pid for pid, reason in recommendations_with_reasons]
        products = Product.objects.filter(id__in=recommended_ids)
        
        # Create recommendation objects with additional info
        recommendations = []
        for product in products:
            # Find the reason for this product
            reason = next((reason for pid, reason in recommendations_with_reasons if pid == product.id), "")
            
            # Get predicted rating
            predicted_rating = engine.predict_rating(user_id, product.id, method='ibcf')
            
            recommendations.append({
                'product': product,
                'reason': reason,
                'predicted_rating': predicted_rating
            })
        
        # Get item similarity matrix (limited for display)
        item_similarity_matrix = engine.calculate_item_similarity()
        if item_similarity_matrix is not None:
            # Limit to first 10 products for display
            limited_matrix = item_similarity_matrix.iloc[:10, :10]
        else:
            limited_matrix = None
        
        # Calculate stats
        total_users = User.objects.count()
        total_products = Product.objects.count()
        avg_similarity = item_similarity_matrix.values.mean() if item_similarity_matrix is not None else 0
        coverage = (len(recommendations) / n_recommendations * 100) if n_recommendations > 0 else 0
        
        context = {
            'recommendations': recommendations,
            'item_similarity_matrix': limited_matrix,
            'total_users': total_users,
            'total_products': total_products,
            'avg_similarity': avg_similarity,
            'coverage': coverage,
            'method': 'IBCF',
        }
        
        return render(request, 'recommendations/ibcf.html', context)
        
    except Exception as e:
        print(f"Error in IBCF recommendations: {str(e)}")
        return render(request, 'recommendations/ibcf.html', {
            'error': 'خطا در تولید توصیه‌ها',
            'total_users': User.objects.count(),
            'total_products': Product.objects.count(),
        })


@csrf_exempt
def predict_rating_api(request, product_id):
    """
    API endpoint to predict rating for a specific product
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    user_id = request.user.id
    method = request.GET.get('method', 'both')  # ubcf, ibcf, or both
    
    engine = RecommendationEngine()
    
    try:
        predicted_rating = engine.predict_rating(user_id, product_id, method=method)
        
        if predicted_rating is not None:
            return JsonResponse({
                'user_id': user_id,
                'product_id': product_id,
                'predicted_rating': round(predicted_rating, 2),
                'method': method,
                'success': True
            })
        else:
            return JsonResponse({
                'user_id': user_id,
                'product_id': product_id,
                'predicted_rating': None,
                'method': method,
                'success': False,
                'message': 'Unable to predict rating'
            })
            
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


def similarity_matrices_view(request):
    """
    View to display similarity matrices
    """
    engine = RecommendationEngine()
    
    try:
        # Calculate matrices
        matrices = engine.get_similarity_matrices()
        
        # Limit matrices for display (first 15x15)
        user_similarity = matrices['user_similarity'].iloc[:15, :15] if matrices['user_similarity'] is not None else None
        item_similarity = matrices['item_similarity'].iloc[:15, :15] if matrices['item_similarity'] is not None else None
        user_item_matrix = matrices['user_item_matrix'].iloc[:15, :15] if matrices['user_item_matrix'] is not None else None
        
        context = {
            'user_similarity_matrix': user_similarity,
            'item_similarity_matrix': item_similarity,
            'user_item_matrix': user_item_matrix,
            'total_users': User.objects.count(),
            'total_products': Product.objects.count(),
        }
        
        return render(request, 'recommendations/similarity_matrices.html', context)
        
    except Exception as e:
        print(f"Error in similarity matrices view: {str(e)}")
        return render(request, 'recommendations/similarity_matrices.html', {
            'error': 'خطا در محاسبه ماتریس‌های شباهت'
        })


@login_required
def cf_dashboard(request):
    """
    Simple dashboard for collaborative filtering
    """
    context = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
    }
    
    return render(request, 'recommendations/cf_dashboard.html', context)
