# Recommendation System Integration Guide

## Overview
This guide explains how to integrate the UBCF and IBCF recommendation system into your Django skincare platform.

## System Architecture

### 1. **Recommendation Engine (`recommendations/engine.py`)**
- **User-Based Collaborative Filtering (UBCF)**: Finds similar users and recommends products they liked
- **Item-Based Collaborative Filtering (IBCF)**: Recommends products similar to what user already likes
- **Content-Based Filtering**: Uses skin profile and product features
- **Hybrid Approach**: Combines multiple methods for better accuracy

### 2. **Data Sources**
- `ProductSearchHistory`: User interactions (views, likes, cart, purchases)
- `ProductPurchaseHistory`: Purchase data with quantities
- `SkinProfile`: User skin assessment data
- `Product`: Product features (category, brand, ingredients, etc.)
- `Comment`: Product ratings and reviews

### 3. **API Endpoints**
- `/recommendations/` - Get personalized recommendations
- `/recommendations/similar/<product_id>/` - Get similar products
- `/recommendations/api/record-interaction/` - Record user interactions
- `/recommendations/dashboard/` - Recommendation dashboard
- `/recommendations/analytics/` - System analytics

## How to Use

### 1. **Install Required Packages**
```bash
pip install -r requirements.txt
```

### 2. **Run Migrations**
```bash
python manage.py migrate
```

### 3. **Generate Sample Data (Optional)**
```bash
python manage.py generate_sample_data --users 100 --interactions 1000
```

### 4. **Add to Templates**

#### Add recommendation section to product pages:
```html
<!-- In product detail template -->
<div id="similar-products">
    <h4>محصولات مشابه</h4>
    <div id="similar-products-container"></div>
</div>

<script>
// Load similar products when page loads
document.addEventListener('DOMContentLoaded', function() {
    const productId = {{ product.id }};
    RecommendationUtils.loadSimilarProducts(productId, 'similar-products-container', 6);
});
</script>
```

#### Add recommendations to user dashboard:
```html
<!-- In user dashboard -->
<div id="user-recommendations">
    <h4>پیشنهادات ویژه برای شما</h4>
    <div id="recommendations-container"></div>
</div>

<script>
RecommendationUtils.loadRecommendations('recommendations-container', 'comprehensive', 8);
</script>
```

### 5. **Track User Interactions**

Include the tracking script in your base template:
```html
<!-- In base.html -->
<script src="{% static 'recommendations/recommendation-tracker.js' %}"></script>
```

Add data attributes to track interactions:
```html
<!-- Product cards -->
<div class="product-card" data-product-id="{{ product.id }}">
    <!-- Product content -->
    <button class="btn btn-primary add-to-cart" data-product-id="{{ product.id }}">
        افزودن به سبد خرید
    </button>
</div>
```

### 6. **Manual Interaction Recording**
```javascript
// Record custom interactions
RecommendationUtils.recordInteraction(productId, 'custom_interaction');
```

## Recommendation Methods

### 1. **User-Based Collaborative Filtering (UBCF)**
```python
engine = RecommendationEngine()
recommendations = engine.user_based_collaborative_filtering(user_id, 10)
```
- Finds users with similar preferences
- Recommends products liked by similar users
- Works best with sufficient user interaction data

### 2. **Item-Based Collaborative Filtering (IBCF)**
```python
recommendations = engine.item_based_collaborative_filtering(user_id, 10)
```
- Finds products similar to user's liked items
- Uses product features and user behavior
- More stable than UBCF

### 3. **Content-Based (Skin Profile)**
```python
recommendations = engine.skin_profile_based_recommendations(user_id, 10)
```
- Uses user's skin type and concerns
- Matches with suitable products
- Works for new users with completed skin profiles

### 4. **Hybrid Approach**
```python
recommendations = engine.hybrid_recommendations(user_id, 10)
```
- Combines UBCF and IBCF
- Provides more diverse recommendations

### 5. **Comprehensive (Recommended)**
```python
recommendations = engine.get_comprehensive_recommendations(user_id, 10)
```
- Uses all methods with optimal weights
- Best overall performance

## URL Integration

Add links to your navigation:
```html
<li><a href="{% url 'recommendations:dashboard' %}">پیشنهادات شخصی</a></li>
<li><a href="{% url 'recommendations:user_recommendations' %}">همه پیشنهادات</a></li>
```

## Performance Optimization

### 1. **Caching**
Add Redis caching for frequent calculations:
```python
from django.core.cache import cache

def get_cached_recommendations(user_id, method='comprehensive'):
    cache_key = f'recommendations_{user_id}_{method}'
    recommendations = cache.get(cache_key)
    
    if not recommendations:
        engine = RecommendationEngine()
        recommendations = engine.get_comprehensive_recommendations(user_id)
        cache.set(cache_key, recommendations, 3600)  # Cache for 1 hour
    
    return recommendations
```

### 2. **Batch Processing**
Process recommendations in background:
```python
# Using Celery for background tasks
@shared_task
def update_user_recommendations(user_id):
    engine = RecommendationEngine()
    recommendations = engine.get_comprehensive_recommendations(user_id)
    cache.set(f'recommendations_{user_id}', recommendations, 86400)
```

### 3. **Database Optimization**
Add database indexes:
```python
# In models.py
class ProductSearchHistory(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['product', 'interaction_type']),
        ]
```

## Monitoring and Analytics

### 1. **View Analytics**
Visit `/recommendations/analytics/` to see:
- Total interactions and purchases
- Interaction type distribution
- Popular products
- System performance metrics

### 2. **Custom Analytics**
```python
from accounts.models import ProductSearchHistory

# Conversion rate
def get_conversion_rate():
    total_views = ProductSearchHistory.objects.filter(interaction_type='view').count()
    total_purchases = ProductSearchHistory.objects.filter(interaction_type='purchase').count()
    return (total_purchases / total_views) * 100 if total_views > 0 else 0
```

## Best Practices

### 1. **Data Quality**
- Ensure user interactions are properly recorded
- Clean and validate interaction data regularly
- Handle missing or incomplete user profiles

### 2. **Cold Start Problem**
- For new users: Use skin profile-based recommendations
- For new products: Use content-based similarity
- Fallback to popular products when no data available

### 3. **Recommendation Diversity**
- Mix different recommendation methods
- Avoid recommending too many similar products
- Include products from different categories

### 4. **Privacy and Ethics**
- Respect user privacy in data collection
- Provide clear opt-out mechanisms
- Explain recommendation rationale to users

## Troubleshooting

### Common Issues:

1. **No recommendations generated**
   - Check if user has sufficient interaction data
   - Verify skin profile completion
   - Check product availability

2. **Poor recommendation quality**
   - Increase user interaction data
   - Tune recommendation weights
   - Improve product features data

3. **Performance issues**
   - Implement caching
   - Optimize database queries
   - Use background processing for heavy calculations

### Debug Mode:
```python
# Enable debug mode in engine
engine = RecommendationEngine()
engine.debug = True
recommendations = engine.get_comprehensive_recommendations(user_id)
```

## Future Enhancements

1. **Deep Learning Integration**
2. **Real-time Recommendations**
3. **A/B Testing Framework**
4. **Advanced Analytics Dashboard**
5. **Multi-arm Bandit Algorithms**
6. **Seasonal and Trending Recommendations**
