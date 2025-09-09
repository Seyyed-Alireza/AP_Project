import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from django.contrib.auth.models import User
from recommendations.engine import RecommendationEngine
from mainpage.models import Product
from accounts.models import ProductSearchHistory

def test_recommendations():
    print("=== Testing Recommendation System ===")
    
    # Get admin user
    try:
        admin = User.objects.get(username='admin')
        print(f"✓ Found admin user: {admin.username} (ID: {admin.id})")
    except User.DoesNotExist:
        print("✗ Admin user not found!")
        return
    
    # Check interactions
    interactions = ProductSearchHistory.objects.filter(user=admin).count()
    print(f"✓ Admin has {interactions} interactions")
    
    # Check products
    total_products = Product.objects.count()
    print(f"✓ Total products in database: {total_products}")
    
    # Test engine
    try:
        engine = RecommendationEngine()
        print("✓ RecommendationEngine created successfully")
        
        # Test matrix creation
        print("\n--- Testing User-Item Matrix ---")
        matrix = engine.create_user_item_matrix()
        print(f"✓ Matrix created: {matrix.shape}")
        print(f"✓ Admin in matrix: {admin.id in matrix.index}")
        
        if admin.id in matrix.index:
            admin_row = matrix.loc[admin.id]
            non_zero = (admin_row > 0).sum()
            print(f"✓ Admin has {non_zero} interactions in matrix")
            print(f"✓ Sample interactions: {admin_row[admin_row > 0].head(3).to_dict()}")
        
        # Test UBCF
        print("\n--- Testing UBCF ---")
        ubcf_recs = engine.user_based_collaborative_filtering(admin.id, 5, True)
        print(f"✓ UBCF returned {len(ubcf_recs)} recommendations")
        
        if ubcf_recs:
            print("✓ Sample recommendations:")
            for i, (product_id, reason) in enumerate(ubcf_recs[:3], 1):
                # Check if product exists
                try:
                    product = Product.objects.get(id=product_id)
                    print(f"  {i}. Product {product_id} ({product.name[:30]}...): {reason[:50]}...")
                except Product.DoesNotExist:
                    print(f"  {i}. Product {product_id} (NOT FOUND IN DB): {reason[:50]}...")
        else:
            print("✗ No UBCF recommendations returned")
            
        # Test fallback
        print("\n--- Testing Fallback ---")
        fallback = engine._get_popular_products_with_reasons(5)
        print(f"✓ Fallback returned {len(fallback)} recommendations")
        if fallback:
            for i, (product_id, reason) in enumerate(fallback[:3], 1):
                print(f"  {i}. Product {product_id}: {reason}")
                
    except Exception as e:
        print(f"✗ Error in recommendation engine: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendations()
