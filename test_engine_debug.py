#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from recommendations.engine import RecommendationEngine
from django.contrib.auth.models import User
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Comment

def test_recommendations():
    print("=== TESTING RECOMMENDATION ENGINE ===")
    
    # Test with admin user (ID 21) who has lots of interactions
    test_user_id = 21
    user = User.objects.get(id=test_user_id)
    print(f"Testing with user: {user.username} (ID: {test_user_id})")
    
    # Check user's interaction data
    search_count = ProductSearchHistory.objects.filter(user_id=test_user_id).count()
    purchase_count = ProductPurchaseHistory.objects.filter(user_id=test_user_id).count()
    comment_count = Comment.objects.filter(user_id=test_user_id).count()
    print(f"User data: {search_count} searches, {purchase_count} purchases, {comment_count} comments")
    
    print("\n--- Creating engine ---")
    engine = RecommendationEngine()
    
    print("\n--- Testing create_user_item_matrix ---")
    try:
        matrix = engine.create_user_item_matrix()
        print(f"Matrix shape: {matrix.shape}")
        print(f"Matrix has {len(matrix)} users and {matrix.shape[1]} products")
        
        # Check if test user is in the matrix
        if test_user_id in matrix.index:
            user_row = matrix.loc[test_user_id]
            non_zero_items = (user_row > 0).sum()
            print(f"Test user has {non_zero_items} interactions in matrix")
        else:
            print(f"Test user {test_user_id} NOT found in matrix!")
            print(f"Matrix users: {list(matrix.index)[:10]}...")
            
    except Exception as e:
        print(f"Matrix creation error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n--- Testing UBCF ---")
    try:
        ubcf_recs = engine.user_based_collaborative_filtering(
            test_user_id, 
            n_recommendations=5,
            include_reasons=True
        )
        print(f"UBCF returned {len(ubcf_recs)} recommendations")
        for i, rec in enumerate(ubcf_recs[:3]):
            print(f"  {i+1}. {rec['product'].name} - {rec['reason']} (Score: {rec['predicted_rating']:.2f})")
    except Exception as e:
        print(f"UBCF Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendations()
