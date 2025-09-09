#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from recommendations.engine import RecommendationEngine
from django.contrib.auth.models import User

def test_recommendations():
    print("=== TESTING RECOMMENDATION ENGINE ===")
    
    # Test with admin user (ID 21) who has lots of interactions
    test_user_id = 21
    user = User.objects.get(id=test_user_id)
    print(f"Testing with user: {user.username} (ID: {test_user_id})")
    
    engine = RecommendationEngine()
    
    print("\n1. Testing User-Based Collaborative Filtering...")
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
    
    print("\n2. Testing Item-Based Collaborative Filtering...")
    try:
        ibcf_recs = engine.item_based_collaborative_filtering(
            test_user_id, 
            n_recommendations=5,
            include_reasons=True
        )
        print(f"IBCF returned {len(ibcf_recs)} recommendations")
        for i, rec in enumerate(ibcf_recs[:3]):
            print(f"  {i+1}. {rec['product'].name} - {rec['reason']} (Score: {rec['predicted_rating']:.2f})")
    except Exception as e:
        print(f"IBCF Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendations()
