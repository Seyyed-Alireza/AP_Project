from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from mainpage.models import Product
from .collaborative_filtering import CollaborativeFilteringEngine
import json


@login_required
def get_ubcf_recommendations(request):
    """
    Get User-Based Collaborative Filtering recommendations
    """
    user_id = request.user.id
    n_recommendations = int(request.GET.get('count', 10))
    k_users = int(request.GET.get('k_users', 50))
    
    cf_engine = CollaborativeFilteringEngine(debug=True)
    
    try:
        # Get UBCF recommendations
        recommendations = cf_engine.get_ubcf_recommendations(
            user_id=user_id, 
            n_recommendations=n_recommendations,
            k_users=k_users
        )
        
        # Get product objects and add prediction info
        products_with_predictions = []
        for rec in recommendations:
            try:
                product = Product.objects.get(id=rec['product_id'])
                products_with_predictions.append({
                    'product': product,
                    'predicted_rating': rec['predicted_rating'],
                    'reasoning': rec['reasoning'],
                    'method': rec['method']
                })
            except Product.DoesNotExist:
                continue
        
        # Get similarity info for debugging
        similarity_info = cf_engine.get_similarity_info(user_id=user_id)
        
        context = {
            'recommendations': products_with_predictions,
            'method': 'UBCF',
            'method_name': 'فیلترینگ مشارکتی بر اساس کاربر',
            'similarity_info': similarity_info,
            'k_users': k_users
        }
        
        if request.headers.get('Accept') == 'application/json':
            # Return JSON response for API calls
            products_data = []
            for item in products_with_predictions:
                product = item['product']
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'price': product.price,
                    'rating': product.rating,
                    'predicted_rating': item['predicted_rating'],
                    'image_url': product.image.url if product.image else None,
                    'category': product.get_category_display_fa(),
                    'reasoning': item['reasoning'],
                })
            
            return JsonResponse({
                'status': 'success',
                'method': 'UBCF',
                'products': products_data,
                'similarity_info': similarity_info,
                'count': len(products_data)
            })
        else:
            return render(request, 'recommendations/cf_recommendations.html', context)
    
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        else:
            return render(request, 'recommendations/error_page.html', {'error': str(e)})


@login_required
def get_ibcf_recommendations(request):
    """
    Get Item-Based Collaborative Filtering recommendations
    """
    user_id = request.user.id
    n_recommendations = int(request.GET.get('count', 10))
    k_items = int(request.GET.get('k_items', 50))
    
    cf_engine = CollaborativeFilteringEngine(debug=True)
    
    try:
        # Get IBCF recommendations
        recommendations = cf_engine.get_ibcf_recommendations(
            user_id=user_id, 
            n_recommendations=n_recommendations,
            k_items=k_items
        )
        
        # Get product objects and add prediction info
        products_with_predictions = []
        for rec in recommendations:
            try:
                product = Product.objects.get(id=rec['product_id'])
                products_with_predictions.append({
                    'product': product,
                    'predicted_rating': rec['predicted_rating'],
                    'reasoning': rec['reasoning'],
                    'method': rec['method']
                })
            except Product.DoesNotExist:
                continue
        
        # Get similarity info for debugging
        similarity_info = cf_engine.get_similarity_info(user_id=user_id)
        
        context = {
            'recommendations': products_with_predictions,
            'method': 'IBCF',
            'method_name': 'فیلترینگ مشارکتی بر اساس آیتم',
            'similarity_info': similarity_info,
            'k_items': k_items
        }
        
        if request.headers.get('Accept') == 'application/json':
            # Return JSON response for API calls
            products_data = []
            for item in products_with_predictions:
                product = item['product']
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'price': product.price,
                    'rating': product.rating,
                    'predicted_rating': item['predicted_rating'],
                    'image_url': product.image.url if product.image else None,
                    'category': product.get_category_display_fa(),
                    'reasoning': item['reasoning'],
                })
            
            return JsonResponse({
                'status': 'success',
                'method': 'IBCF',
                'products': products_data,
                'similarity_info': similarity_info,
                'count': len(products_data)
            })
        else:
            return render(request, 'recommendations/cf_recommendations.html', context)
    
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        else:
            return render(request, 'recommendations/error_page.html', {'error': str(e)})


@login_required
def predict_rating(request, product_id):
    """
    Predict user rating for a specific product using both UBCF and IBCF
    """
    user_id = request.user.id
    method = request.GET.get('method', 'both')  # ubcf, ibcf, or both
    
    cf_engine = CollaborativeFilteringEngine(debug=True)
    
    try:
        product = get_object_or_404(Product, id=product_id)
        predictions = {}
        
        if method in ['ubcf', 'both']:
            ubcf_rating = cf_engine.predict_rating_ubcf(user_id, product_id)
            ubcf_reason = cf_engine._get_ubcf_reason(user_id, product_id)
            predictions['ubcf'] = {
                'rating': ubcf_rating,
                'reasoning': ubcf_reason
            }
        
        if method in ['ibcf', 'both']:
            ibcf_rating = cf_engine.predict_rating_ibcf(user_id, product_id)
            ibcf_reason = cf_engine._get_ibcf_reason(user_id, product_id)
            predictions['ibcf'] = {
                'rating': ibcf_rating,
                'reasoning': ibcf_reason
            }
        
        # Calculate average if both methods
        if method == 'both' and 'ubcf' in predictions and 'ibcf' in predictions:
            avg_rating = (predictions['ubcf']['rating'] + predictions['ibcf']['rating']) / 2
            predictions['average'] = {
                'rating': avg_rating,
                'reasoning': 'میانگین پیش‌بینی UBCF و IBCF'
            }
        
        # Get similarity info
        similarity_info = cf_engine.get_similarity_info(user_id=user_id, item_id=product_id)
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'success',
                'product_id': product_id,
                'product_name': product.name,
                'predictions': predictions,
                'similarity_info': similarity_info
            })
        else:
            context = {
                'product': product,
                'predictions': predictions,
                'similarity_info': similarity_info,
                'method': method
            }
            return render(request, 'recommendations/rating_prediction.html', context)
    
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        else:
            return render(request, 'recommendations/error_page.html', {'error': str(e)})


@login_required
def similarity_matrices_view(request):
    """
    View to display similarity matrices information
    """
    cf_engine = CollaborativeFilteringEngine(debug=True)
    
    try:
        # Create matrices
        user_item_matrix = cf_engine.create_user_item_matrix()
        user_similarity = cf_engine.calculate_user_similarity()
        item_similarity = cf_engine.calculate_item_similarity()
        
        # Get matrix info
        similarity_info = cf_engine.get_similarity_info(user_id=request.user.id)
        
        # Get top similar users and items for current user
        top_similar_users = None
        top_similar_items = None
        
        if request.user.id in user_similarity.index:
            top_similar_users = user_similarity.loc[request.user.id].nlargest(6)[1:].to_dict()
        
        # Get user's rated items to find similar items
        if request.user.id in user_item_matrix.index:
            user_ratings = user_item_matrix.loc[request.user.id]
            rated_items = user_ratings[user_ratings > 0].index
            
            if len(rated_items) > 0:
                # Get similarities for first rated item
                first_item = rated_items[0]
                if first_item in item_similarity.index:
                    top_similar_items = item_similarity.loc[first_item].nlargest(6)[1:].to_dict()
        
        context = {
            'similarity_info': similarity_info,
            'top_similar_users': top_similar_users,
            'top_similar_items': top_similar_items,
            'user_item_matrix_sample': user_item_matrix.head(10).to_html() if not user_item_matrix.empty else None,
        }
        
        return render(request, 'recommendations/similarity_matrices.html', context)
    
    except Exception as e:
        return render(request, 'recommendations/error_page.html', {'error': str(e)})


@login_required
def cf_dashboard(request):
    """
    Collaborative Filtering dashboard with both UBCF and IBCF
    """
    user_id = request.user.id
    cf_engine = CollaborativeFilteringEngine(debug=True)
    
    try:
        # Get both types of recommendations
        ubcf_recs = cf_engine.get_ubcf_recommendations(user_id, n_recommendations=5)
        ibcf_recs = cf_engine.get_ibcf_recommendations(user_id, n_recommendations=5)
        
        # Convert to product objects
        ubcf_products = []
        for rec in ubcf_recs:
            try:
                product = Product.objects.get(id=rec['product_id'])
                ubcf_products.append({
                    'product': product,
                    'predicted_rating': rec['predicted_rating'],
                    'reasoning': rec['reasoning']
                })
            except Product.DoesNotExist:
                continue
        
        ibcf_products = []
        for rec in ibcf_recs:
            try:
                product = Product.objects.get(id=rec['product_id'])
                ibcf_products.append({
                    'product': product,
                    'predicted_rating': rec['predicted_rating'],
                    'reasoning': rec['reasoning']
                })
            except Product.DoesNotExist:
                continue
        
        # Get similarity info
        similarity_info = cf_engine.get_similarity_info(user_id=user_id)
        
        context = {
            'ubcf_recommendations': ubcf_products,
            'ibcf_recommendations': ibcf_products,
            'similarity_info': similarity_info
        }
        
        return render(request, 'recommendations/cf_dashboard.html', context)
    
    except Exception as e:
        return render(request, 'recommendations/error_page.html', {'error': str(e)})
