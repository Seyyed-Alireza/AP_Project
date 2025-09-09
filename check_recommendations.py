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
from collections import Counter

print("=== Database Analysis ===")
print(f"Total users: {User.objects.count()}")
print(f"Total products: {Product.objects.count()}")
print(f"Total interactions: {ProductSearchHistory.objects.count()}")
print(f"Total purchases: {ProductPurchaseHistory.objects.count()}")
print(f"Total comments: {Comment.objects.count()}")

print("\n=== Interaction Distribution ===")
interactions = ProductSearchHistory.objects.all()
interaction_counts = Counter([i.user_id for i in interactions])
print(f"Users with interactions: {len(interaction_counts)}")

if interaction_counts:
    print("Top 5 users by interactions:")
    for user_id, count in interaction_counts.most_common(5):
        try:
            username = User.objects.get(id=user_id).username
            print(f"  User {user_id} ({username}): {count} interactions")
        except User.DoesNotExist:
            print(f"  User {user_id}: {count} interactions")

print("\n=== Recommendation Engine Test ===")
# Test the recommendation engine
from recommendations.engine import RecommendationEngine

engine = RecommendationEngine()
try:
    matrix = engine.create_user_item_matrix()
    print(f"User-item matrix shape: {matrix.shape}")
    print(f"Non-zero entries: {(matrix > 0).sum().sum()}")
    print(f"Matrix density: {(matrix > 0).sum().sum() / (matrix.shape[0] * matrix.shape[1]) * 100:.2f}%")
    
    # Test with the first user who has interactions
    if interaction_counts:
        test_user_id = interaction_counts.most_common(1)[0][0]
        print(f"\n=== Testing recommendations for user {test_user_id} ===")
        
        # Test UBCF
        ubcf_recs = engine.user_based_collaborative_filtering(test_user_id, n_recommendations=5, include_reasons=True)
        print(f"UBCF recommendations: {len(ubcf_recs)}")
        
        # Test IBCF  
        ibcf_recs = engine.item_based_collaborative_filtering(test_user_id, n_recommendations=5, include_reasons=True)
        print(f"IBCF recommendations: {len(ibcf_recs)}")
        
        if ubcf_recs:
            print(f"Sample UBCF recommendation: {ubcf_recs[0]}")
        if ibcf_recs:
            print(f"Sample IBCF recommendation: {ibcf_recs[0]}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n=== Minimum Requirements for Recommendations ===")
print("For UBCF (User-Based Collaborative Filtering):")
print("- Need at least 2 users with similar interactions")
print("- Each user should have interacted with at least 2-3 products")
print("- Similarity threshold > 0.1")

print("\nFor IBCF (Item-Based Collaborative Filtering):")
print("- Current user should have interacted with at least 1 product")
print("- That product should have similarity > 0.1 with other products")
print("- Need sufficient interaction data across products")

print(f"\n=== Action Required ===")
print("Based on your data:")
print(f"- You have {User.objects.count()} users")
print(f"- You have {ProductSearchHistory.objects.count()} interactions") 
print(f"- You have {ProductPurchaseHistory.objects.count()} purchases")
print(f"- You have {Comment.objects.count()} comments")

if ProductSearchHistory.objects.count() < 20:
    print("\n⚠️  RECOMMENDATION: You need more interaction data!")
    print("Suggested actions:")
    print("1. Add more user interactions (search, view, like, cart, purchase)")
    print("2. Add more product ratings/comments")
    print("3. Add purchase history")
    print("4. Ensure current user has interacted with products")
