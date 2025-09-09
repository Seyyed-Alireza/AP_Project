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
from .engine import RecommendationEngine
import json


@login_required
def get_user_recommendations(request):
    """
    Get personalized recommendations for the logged-in user
    """
    user_id = request.user.id
    n_recommendations = int(request.GET.get('count', 10))
    method = request.GET.get('method', 'comprehensive')  # ubcf, ibcf, skin, hybrid, comprehensive
    
    engine = RecommendationEngine()
    
    try:
        if method == 'comprehensive':
            # Use the new advanced comprehensive recommendations
            recommendations = engine.hybrid_recommendations(
                user_id=user_id, 
                n_recommendations=n_recommendations, 
                with_reasons=True
            )
            
            # Convert to the expected format
            recommended_ids = [rec['product_id'] for rec in recommendations]
            recommendation_reasons = {rec['product_id']: rec['reasoning'] for rec in recommendations}
            
        elif method == 'ubcf':
            recommendations_with_reasons = engine.user_based_collaborative_filtering(user_id, n_recommendations, include_reasons=True)
            recommended_ids = [pid for pid, reason in recommendations_with_reasons]
            recommendation_reasons = {pid: reason for pid, reason in recommendations_with_reasons}
        elif method == 'ibcf':
            recommendations_with_reasons = engine.item_based_collaborative_filtering(user_id, n_recommendations, include_reasons=True)
            recommended_ids = [pid for pid, reason in recommendations_with_reasons]
            recommendation_reasons = {pid: reason for pid, reason in recommendations_with_reasons}
        elif method == 'skin':
            recommendations_with_reasons = engine.skin_profile_based_recommendations(user_id, n_recommendations, include_reasons=True)
            recommended_ids = [pid for pid, reason in recommendations_with_reasons]
            recommendation_reasons = {pid: reason for pid, reason in recommendations_with_reasons}
        else:  # hybrid
            recommended_ids = engine.hybrid_recommendations(user_id, n_recommendations)
            recommendation_reasons = {pid: "ترکیب روش‌های مختلف پیشنهاد" for pid in recommended_ids}
        
        # Get product objects
        recommended_products = Product.objects.filter(id__in=recommended_ids)
        
        # Order products according to recommendation order and add reasons
        products_dict = {p.id: p for p in recommended_products}
        ordered_products_with_reasons = []
        for pid in recommended_ids:
            if pid in products_dict:
                product = products_dict[pid]
                product.recommendation_reason = recommendation_reasons.get(pid, "")
                ordered_products_with_reasons.append(product)
        
        if request.headers.get('Accept') == 'application/json':
            # Return JSON response for API calls
            products_data = []
            for product in ordered_products_with_reasons:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'price': product.price,
                    'rating': product.rating,
                    'image_url': product.image.url if product.image else None,
                    'category': product.get_category_display_fa(),
                    'skin_types': product.get_skin_types_fa(),
                    'reason': getattr(product, 'recommendation_reason', ''),
                })
            
            return JsonResponse({
                'status': 'success',
                'method': method,
                'products': products_data,
                'count': len(products_data)
            })
        else:
            # Return HTML response
            context = {
                'recommended_products': ordered_products_with_reasons,
                'method': method,
                'method_name': get_method_name(method)
            }
            return render(request, 'recommendations/user_recommendations.html', context)
    
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        else:
            return render(request, 'recommendations/error_page.html', {'error': str(e)})


def get_similar_products(request, product_id):
    """
    Get products similar to a specific product (IBCF for single product)
    """
    n_recommendations = int(request.GET.get('count', 6))
    
    try:
        target_product = get_object_or_404(Product, id=product_id)
        engine = RecommendationEngine()
        
        # Calculate item similarity matrix
        engine.create_item_features_matrix()
        engine.calculate_item_similarity()
        
        if product_id not in engine.item_similarity_matrix.index:
            # Fallback to products in same category
            similar_products = Product.objects.filter(
                category=target_product.category
            ).exclude(id=product_id).order_by('-rating')[:n_recommendations]
            # Add reason for fallback products
            for product in similar_products:
                product.similarity_reason = f"همان دسته‌بندی ({target_product.get_category_display_fa()})"
        else:
            # Get similar products using item similarity
            similarities = engine.item_similarity_matrix.loc[product_id].sort_values(ascending=False)[1:n_recommendations+1]
            similar_product_ids = similarities.index.tolist()
            similarity_scores = similarities.values.tolist()
            
            # Get product objects
            similar_products = Product.objects.filter(id__in=similar_product_ids)
            products_dict = {p.id: p for p in similar_products}
            similar_products = []
            
            for i, pid in enumerate(similar_product_ids):
                if pid in products_dict:
                    product = products_dict[pid]
                    similarity_score = similarity_scores[i]
                    
                    # Create similarity reason
                    if similarity_score > 0.8:
                        reason = "بسیار شبیه به این محصول"
                    elif similarity_score > 0.6:
                        reason = "شباهت زیاد در ویژگی‌ها"
                    elif similarity_score > 0.4:
                        reason = "شباهت متوسط در کاربرد"
                    else:
                        reason = "شباهت در دسته‌بندی"
                    
                    product.similarity_reason = reason
                    product.similarity_score = similarity_score
                    similar_products.append(product)
        
        if request.headers.get('Accept') == 'application/json':
            products_data = []
            for product in similar_products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'price': product.price,
                    'rating': product.rating,
                    'image_url': product.image.url if product.image else None,
                    'category': product.get_category_display_fa(),
                })
            
            return JsonResponse({
                'status': 'success',
                'target_product': target_product.name,
                'similar_products': products_data,
                'count': len(products_data)
            })
        else:
            context = {
                'target_product': target_product,
                'similar_products': similar_products
            }
            return render(request, 'recommendations/similar_products.html', context)
    
    except Exception as e:
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        else:
            return render(request, 'recommendations/error_page.html', {'error': str(e)})


@api_view(['POST'])
def record_interaction(request):
    """
    Record user interaction with a product for improving recommendations
    """
    from accounts.models import ProductSearchHistory
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        interaction_type = data.get('interaction_type', 'view')  # view, like, cart, etc.
        
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.is_authenticated:
            product = get_object_or_404(Product, id=product_id)
            
            # Record the interaction
            ProductSearchHistory.objects.create(
                user=request.user,
                product=product,
                interaction_type=interaction_type
            )
            
            return Response({'status': 'success', 'message': 'Interaction recorded'})
        else:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
def recommendations_dashboard(request):
    """
    Dashboard showing different types of recommendations
    """
    user_id = request.user.id
    engine = RecommendationEngine()
    
    try:
        # Get different types of recommendations
        ubcf_recs = engine.user_based_collaborative_filtering(user_id, 5)
        ibcf_recs = engine.item_based_collaborative_filtering(user_id, 5)
        skin_recs = engine.skin_profile_based_recommendations(user_id, 5)
        comprehensive_recs = engine.get_comprehensive_recommendations(user_id, 10)
        
        # Get product objects for each recommendation type
        contexts = {}
        
        for rec_type, rec_ids in [
            ('ubcf', ubcf_recs),
            ('ibcf', ibcf_recs),
            ('skin', skin_recs),
            ('comprehensive', comprehensive_recs)
        ]:
            products = Product.objects.filter(id__in=rec_ids)
            products_dict = {p.id: p for p in products}
            ordered_products = [products_dict[pid] for pid in rec_ids if pid in products_dict]
            contexts[f'{rec_type}_products'] = ordered_products
        
        return render(request, 'recommendations/dashboard.html', contexts)
    
    except Exception as e:
        return render(request, 'recommendations/error_page.html', {'error': str(e)})


def get_method_name(method):
    """Helper function to get user-friendly method names"""
    method_names = {
        'ubcf': 'بر اساس کاربران مشابه',
        'ibcf': 'بر اساس محصولات مشابه',
        'skin': 'بر اساس پروفایل پوست',
        'hybrid': 'ترکیبی',
        'comprehensive': 'جامع'
    }
    return method_names.get(method, 'نامشخص')


class RecommendationAnalytics(View):
    """
    Analytics view for recommendation system performance
    """
    
    @method_decorator(login_required)
    def get(self, request):
        from django.db.models import Count, Avg
        from accounts.models import ProductSearchHistory, ProductPurchaseHistory
        
        # Basic analytics
        total_interactions = ProductSearchHistory.objects.count()
        total_purchases = ProductPurchaseHistory.objects.count()
        active_users = ProductSearchHistory.objects.values('user').distinct().count()
        
        # Interaction type distribution
        interaction_stats = ProductSearchHistory.objects.values('interaction_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Most popular products
        popular_products = Product.objects.annotate(
            interaction_count=Count('browsing_histories')
        ).order_by('-interaction_count')[:10]
        
        context = {
            'total_interactions': total_interactions,
            'total_purchases': total_purchases,
            'active_users': active_users,
            'interaction_stats': interaction_stats,
            'popular_products': popular_products,
        }
        
        return render(request, 'recommendations/analytics_page.html', context)
