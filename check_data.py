#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Comment

# Check current data
print("=== CURRENT DATABASE STATUS ===")
print(f"Total users: {User.objects.count()}")
print(f"Total search interactions: {ProductSearchHistory.objects.count()}")
print(f"Total purchases: {ProductPurchaseHistory.objects.count()}")
print(f"Total comments: {Comment.objects.count()}")

# Check users with data
users_with_searches = User.objects.filter(searches__isnull=False).distinct().count()
users_with_purchases = User.objects.filter(purchases_histories__isnull=False).distinct().count()
users_with_comments = User.objects.filter(comment__isnull=False).distinct().count()

print(f"\nUsers with search data: {users_with_searches}")
print(f"Users with purchase data: {users_with_purchases}")
print(f"Users with comment data: {users_with_comments}")

# Check a few specific users
print("\n=== SAMPLE USER DATA ===")
for user in User.objects.all()[:10]:
    search_count = ProductSearchHistory.objects.filter(user=user).count()
    purchase_count = ProductPurchaseHistory.objects.filter(user=user).count()
    comment_count = Comment.objects.filter(user=user).count()
    total = search_count + purchase_count + comment_count
    if total > 0:
        print(f"User {user.id} ({user.username}): {search_count} searches, {purchase_count} purchases, {comment_count} comments = {total} total")

print("\n✅ Data check complete!")
