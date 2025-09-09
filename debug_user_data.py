#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Comment

def main():
    print("=== DEBUG USER DATA ===")
    
    # Check total counts
    print(f"Total users: {User.objects.count()}")
    print(f"Total search history: {ProductSearchHistory.objects.count()}")
    print(f"Total purchase history: {ProductPurchaseHistory.objects.count()}")
    print(f"Total comments: {Comment.objects.count()}")
    
    # Check users with interactions
    users_with_data = []
    for user in User.objects.all():
        search_count = ProductSearchHistory.objects.filter(user=user).count()
        purchase_count = ProductPurchaseHistory.objects.filter(user=user).count()
        comment_count = Comment.objects.filter(user=user).count()
        
        if search_count > 0 or purchase_count > 0 or comment_count > 0:
            users_with_data.append({
                'user': user,
                'searches': search_count,
                'purchases': purchase_count,
                'comments': comment_count
            })
    
    print(f"\nUsers with interaction data: {len(users_with_data)}")
    
    # Show first 10 users with data
    for i, user_data in enumerate(users_with_data[:10]):
        user = user_data['user']
        print(f"User {user.id} ({user.username}): {user_data['searches']} searches, {user_data['purchases']} purchases, {user_data['comments']} comments")
    
    # Check if specific users exist from our synthetic data
    synthetic_users = User.objects.filter(username__startswith='skincare_user_')
    print(f"\nSynthetic users found: {synthetic_users.count()}")
    
    if synthetic_users.exists():
        for user in synthetic_users[:5]:
            search_count = ProductSearchHistory.objects.filter(user=user).count()
            print(f"  {user.username}: {search_count} searches")

if __name__ == "__main__":
    main()
