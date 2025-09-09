import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from django.contrib.auth.models import User
from mainpage.models import Product

# Simple test
print("=== Simple Test ===")

# Test 1: Check admin user
try:
    admin = User.objects.get(username='admin')
    print(f"Admin found: {admin.username} (ID: {admin.id})")
except Exception as e:
    print(f"Admin error: {e}")

# Test 2: Check products
try:
    product_count = Product.objects.count()
    print(f"Products: {product_count}")
    
    # Get a few sample products
    sample_products = Product.objects.all()[:5]
    print("Sample products:")
    for p in sample_products:
        print(f"  - {p.id}: {p.name}")
        
except Exception as e:
    print(f"Products error: {e}")

# Test 3: Try to get popular products directly
try:
    from django.db.models import F
    popular_products = Product.objects.annotate(
        popularity_score=F('sales_count') + F('rating') * 10
    ).order_by('-popularity_score')[:5]
    
    print("Popular products:")
    for p in popular_products:
        print(f"  - {p.id}: {p.name} (Score: {p.sales_count + p.rating * 10})")
        
except Exception as e:
    print(f"Popular products error: {e}")

print("Simple test completed.")
