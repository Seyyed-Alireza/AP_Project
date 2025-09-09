#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Comment, Product
from django.contrib.auth.models import User
from recommendations.engine import RecommendationEngine

# Get admin user
admin_user = User.objects.get(username='admin')
print(f"=== Testing Recommendations for Admin User (ID: {admin_user.id}) ===")

# Check admin's interaction data
interactions = ProductSearchHistory.objects.filter(user=admin_user)
purchases = ProductPurchaseHistory.objects.filter(user=admin_user)
comments = Comment.objects.filter(user=admin_user)

print(f"Admin interactions: {interactions.count()}")
print(f"Admin purchases: {purchases.count()}")
print(f"Admin comments: {comments.count()}")

if interactions.exists():
    print(f"\nFirst 5 interactions:")
    for i, interaction in enumerate(interactions[:5]):
        print(f"  {i+1}. Product {interaction.product_id} - Type: {interaction.interaction_type}")

# Test recommendation engine step by step
print(f"\n=== Testing Recommendation Engine ===")
engine = RecommendationEngine()

print("1. Creating user-item matrix...")
try:
    matrix = engine.create_user_item_matrix()
    print(f"   Matrix shape: {matrix.shape}")
    print(f"   Admin user in matrix: {admin_user.id in matrix.index}")
    
    if admin_user.id in matrix.index:
        admin_row = matrix.loc[admin_user.id]
        non_zero_products = admin_row[admin_row > 0]
        print(f"   Admin's non-zero interactions: {len(non_zero_products)}")
        if len(non_zero_products) > 0:
            print(f"   Sample interactions:")
            for product_id, score in non_zero_products.head(5).items():
                print(f"     Product {product_id}: {score}")
    
except Exception as e:
    print(f"   Error creating matrix: {e}")

print("\n2. Testing UBCF...")
try:
    # Test user similarity calculation
    user_sim = engine.calculate_user_similarity()
    print(f"   User similarity matrix shape: {user_sim.shape}")
    
    if admin_user.id in user_sim.index:
        admin_similarities = user_sim[admin_user.id].sort_values(ascending=False)[1:6]  # Top 5 similar users
        print(f"   Top 5 similar users to admin:")
        for user_id, similarity in admin_similarities.items():
            try:
                username = User.objects.get(id=user_id).username
                print(f"     User {user_id} ({username}): {similarity:.3f}")
            except:
                print(f"     User {user_id}: {similarity:.3f}")
    
    # Test UBCF recommendations
    ubcf_recs = engine.user_based_collaborative_filtering(admin_user.id, n_recommendations=5, include_reasons=True)
    print(f"   UBCF recommendations count: {len(ubcf_recs)}")
    
    if ubcf_recs:
        print(f"   Sample UBCF recommendations:")
        for i, (product_id, reason) in enumerate(ubcf_recs[:3]):
            try:
                product = Product.objects.get(id=product_id)
                print(f"     {i+1}. Product {product_id} ({product.name[:30]}...)")
                print(f"        Reason: {reason}")
            except:
                print(f"     {i+1}. Product {product_id}")
                print(f"        Reason: {reason}")
    else:
        print("   No UBCF recommendations generated")
        
except Exception as e:
    print(f"   Error in UBCF: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Testing IBCF...")
try:
    # Test item similarity calculation
    item_sim = engine.calculate_item_similarity()
    print(f"   Item similarity matrix shape: {item_sim.shape}")
    
    # Test IBCF recommendations
    ibcf_recs = engine.item_based_collaborative_filtering(admin_user.id, n_recommendations=5, include_reasons=True)
    print(f"   IBCF recommendations count: {len(ibcf_recs)}")
    
    if ibcf_recs:
        print(f"   Sample IBCF recommendations:")
        for i, (product_id, reason) in enumerate(ibcf_recs[:3]):
            try:
                product = Product.objects.get(id=product_id)
                print(f"     {i+1}. Product {product_id} ({product.name[:30]}...)")
                print(f"        Reason: {reason}")
            except:
                print(f"     {i+1}. Product {product_id}")
                print(f"        Reason: {reason}")
    else:
        print("   No IBCF recommendations generated")
        
except Exception as e:
    print(f"   Error in IBCF: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Debugging Information ===")
print("Checking for common issues:")

# Check if products exist
if not Product.objects.exists():
    print("❌ No products in database")
else:
    print(f"✅ {Product.objects.count()} products in database")

# Check if other users have interactions
other_user_interactions = ProductSearchHistory.objects.exclude(user=admin_user).count()
print(f"✅ {other_user_interactions} interactions from other users")

# Check interaction types
interaction_types = interactions.values_list('interaction_type', flat=True).distinct()
print(f"✅ Admin interaction types: {list(interaction_types)}")

print("\n=== Potential Issues ===")
if interactions.count() < 5:
    print("⚠️  Admin has very few interactions")
if other_user_interactions < 10:
    print("⚠️  Very few interactions from other users")
if purchases.count() == 0 and comments.count() == 0:
    print("⚠️  Admin has no purchases or ratings - only search interactions")
