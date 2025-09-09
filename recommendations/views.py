from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from mainpage.models import Product
from .engine import RecommendationEngine
import json
import pandas as pd


def test_view(request):
    """
    Simple test view
    """
    print("[DEBUG] Test view called!")
    return HttpResponse("Test view works! User: " + str(request.user.username if request.user.is_authenticated else 'Anonymous'))


def ubcf_recommendations(request):
    """
    User-Based Collaborative Filtering recommendations view
    """
    print(f"[DEBUG] UBCF view called! User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    
    if not request.user.is_authenticated:
        print("[DEBUG] User not authenticated, redirecting...")
        from django.shortcuts import redirect
        return redirect('accounts:login')
    
    user_id = request.user.id
    n_recommendations = int(request.GET.get('count', 10))
    
    try:
        # Use actual UBCF algorithm
        print(f"[DEBUG] Getting UBCF recommendations for user {user_id}")
        
        engine = RecommendationEngine()
        ubcf_recommendations = engine.user_based_collaborative_filtering(
            user_id, 
            n_recommendations=n_recommendations,
            include_reasons=True
        )
        
        print(f"[DEBUG] UBCF engine returned {len(ubcf_recommendations)} recommendations")
        
        # If no recommendations from UBCF, fall back to popular products
        if not ubcf_recommendations:
            print("[DEBUG] No UBCF recommendations, falling back to popular products")
            from django.db.models import F
            popular_products = Product.objects.annotate(
                popularity_score=F('sales_count') + F('rating') * 10
            ).order_by('-popularity_score')[:n_recommendations]
            
            recommendations = []
            for product in popular_products:
                recommendations.append({
                    'product': product,
                    'reason': f"محصول محبوب (عدم داده کافی برای UBCF) | امتیاز: {product.rating:.1f}",
                    'predicted_rating': product.rating
                })
        else:
            recommendations = ubcf_recommendations
            
        print(f"[DEBUG] Final UBCF recommendations list has {len(recommendations)} items")
        
        # Calculate stats
        total_users = User.objects.count()
        total_products = Product.objects.count()
        
        # Get user similarity matrix for display
        user_similarity_matrix = engine.calculate_user_similarity()
        display_matrix = user_similarity_matrix.iloc[:15, :15] if user_similarity_matrix is not None else None
        
        avg_similarity = user_similarity_matrix.values.mean() if user_similarity_matrix is not None else 0
        coverage = (len(recommendations) / n_recommendations * 100) if n_recommendations > 0 else 0
        
        context = {
            'recommendations': recommendations,
            'user_similarity_matrix': display_matrix,
            'total_users': total_users,
            'total_products': total_products,
            'avg_similarity': round(avg_similarity, 3),
            'coverage': round(coverage, 1),
            'method': 'UBCF',
        }
        
        return render(request, 'recommendations/ubcf.html', context)
        
    except Exception as e:
        print(f"Error in UBCF recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return render(request, 'recommendations/ubcf.html', {
            'error': f'خطا در تولید توصیه‌های UBCF: {str(e)}',
            'total_users': User.objects.count(),
            'total_products': Product.objects.count(),
        })


def ibcf_recommendations(request):
    """
    Item-Based Collaborative Filtering recommendations view
    """
    print(f"[DEBUG] IBCF view called! User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
    
    if not request.user.is_authenticated:
        print("[DEBUG] User not authenticated, redirecting...")
        from django.shortcuts import redirect
        return redirect('accounts:login')
    
    user_id = request.user.id
    n_recommendations = int(request.GET.get('count', 10))
    
    try:
        # Use actual IBCF algorithm
        print(f"[DEBUG] Getting IBCF recommendations for user {user_id}")
        
        engine = RecommendationEngine()
        ibcf_recommendations = engine.item_based_collaborative_filtering(
            user_id, 
            n_recommendations=n_recommendations,
            include_reasons=True
        )
        
        print(f"[DEBUG] IBCF engine returned {len(ibcf_recommendations)} recommendations")
        
        # If no recommendations from IBCF, fall back to popular products
        if not ibcf_recommendations:
            print("[DEBUG] No IBCF recommendations, falling back to popular products")
            from django.db.models import F
            popular_products = Product.objects.annotate(
                popularity_score=F('sales_count') + F('rating') * 10
            ).order_by('-popularity_score')[:n_recommendations]
            
            recommendations = []
            for product in popular_products:
                recommendations.append({
                    'product': product,
                    'reason': f"محصول محبوب (عدم داده کافی برای IBCF) | امتیاز: {product.rating:.1f}",
                    'predicted_rating': product.rating
                })
        else:
            recommendations = ibcf_recommendations
            
        print(f"[DEBUG] Final IBCF recommendations list has {len(recommendations)} items")
        
        # Calculate stats
        total_users = User.objects.count()
        total_products = Product.objects.count()
        
        # Get item similarity matrix for display
        item_similarity_matrix = engine.calculate_item_similarity()
        display_matrix = item_similarity_matrix.iloc[:15, :15] if item_similarity_matrix is not None else None
        
        avg_similarity = item_similarity_matrix.values.mean() if item_similarity_matrix is not None else 0
        coverage = (len(recommendations) / n_recommendations * 100) if n_recommendations > 0 else 0
        
        context = {
            'recommendations': recommendations,
            'item_similarity_matrix': display_matrix,
            'total_users': total_users,
            'total_products': total_products,
            'avg_similarity': round(avg_similarity, 3),
            'coverage': round(coverage, 1),
            'method': 'IBCF',
        }
        
        return render(request, 'recommendations/ibcf.html', context)
        
    except Exception as e:
        print(f"Error in IBCF recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return render(request, 'recommendations/ibcf.html', {
            'error': f'خطا در تولید توصیه‌های IBCF: {str(e)}',
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
            'total_possible_relations': User.objects.count() * Product.objects.count(),
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
    total_users = User.objects.count()
    total_products = Product.objects.count()
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_possible_relations': total_users * total_products,
    }
    
    return render(request, 'recommendations/cf_dashboard.html', context)
