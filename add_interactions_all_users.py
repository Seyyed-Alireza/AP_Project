#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Product, Comment
from datetime import datetime, timedelta
import random

def add_interactions_for_all_users():
    """Add random interactions for all users who don't have any data"""
    print("=== ADDING INTERACTIONS FOR ALL USERS ===\n")
    
    # Get all products for random selection
    products = list(Product.objects.all())
    if not products:
        print("❌ No products found! Please add products first.")
        return
    
    print(f"📦 Found {len(products)} products to use for interactions")
    
    # Get all users
    all_users = User.objects.all()
    print(f"👥 Found {all_users.count()} total users")
    
    users_updated = 0
    
    for user in all_users:
        # Check if user already has interactions
        search_count = ProductSearchHistory.objects.filter(user=user).count()
        purchase_count = ProductPurchaseHistory.objects.filter(user=user).count()
        comment_count = Comment.objects.filter(user=user).count()
        
        if search_count > 0 or purchase_count > 0 or comment_count > 0:
            print(f"⏭️  Skipping {user.username} (already has {search_count + purchase_count + comment_count} interactions)")
            continue
        
        try:
            # Generate random number of interactions for each user
            num_searches = random.randint(10, 50)  # 10-50 search interactions
            num_purchases = random.randint(1, 8)   # 1-8 purchases
            num_comments = random.randint(0, 5)    # 0-5 comments
            
            # Add search history with different interaction types
            interaction_types = ['view', 'like', 'cart', 'wishlist']
            for i in range(num_searches):
                product = random.choice(products)
                ProductSearchHistory.objects.create(
                    user=user,
                    product=product,
                    interaction_type=random.choice(interaction_types),
                    searched_at=datetime.now() - timedelta(days=random.randint(1, 90))
                )
            
            # Add purchase history with ratings
            purchased_products = random.sample(products, min(num_purchases, len(products)))
            for product in purchased_products:
                rating = round(random.uniform(2.5, 5.0), 1)  # Ratings between 2.5-5.0
                ProductPurchaseHistory.objects.create(
                    user=user,
                    product=product,
                    rating=rating,
                    purchased_at=datetime.now() - timedelta(days=random.randint(1, 60))
                )
            
            # Add comments
            for i in range(num_comments):
                product = random.choice(products)
                rating = round(random.uniform(3.0, 5.0), 1)
                comments_list = [
                    f"Great product! Really loved it. Rating: {rating}/5",
                    f"Good quality, would recommend. {rating} stars!",
                    f"Nice skincare product, works well. {rating}/5",
                    f"Satisfied with this purchase. {rating} stars",
                    f"Excellent for my skin type. {rating}/5 stars",
                    f"Works as expected, good value. Rating: {rating}",
                ]
                Comment.objects.create(
                    user=user,
                    product=product,
                    content=random.choice(comments_list),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 45))
                )
            
            users_updated += 1
            print(f"✅ Added data for {user.username}: {num_searches} searches, {num_purchases} purchases, {num_comments} comments")
            
            # Show progress every 50 users
            if users_updated % 50 == 0:
                print(f"\n📊 Progress: {users_updated} users completed...\n")
                
        except Exception as e:
            print(f"❌ Error adding data for {user.username}: {e}")
    
    print(f"\n🎉 COMPLETED! Added interactions for {users_updated} users")
    
    # Show final statistics
    total_searches = ProductSearchHistory.objects.count()
    total_purchases = ProductPurchaseHistory.objects.count()
    total_comments = Comment.objects.count()
    users_with_data = User.objects.filter(
        models.Q(searches__isnull=False) | 
        models.Q(purchases_histories__isnull=False) | 
        models.Q(comment__isnull=False)
    ).distinct().count()
    
    print(f"\n📈 FINAL STATISTICS:")
    print(f"   👥 Users with interaction data: {users_with_data}")
    print(f"   🔍 Total search interactions: {total_searches}")
    print(f"   🛒 Total purchases: {total_purchases}")
    print(f"   💬 Total comments: {total_comments}")
    print(f"   📊 Total interactions: {total_searches + total_purchases + total_comments}")

if __name__ == "__main__":
    # Import Q for the final statistics query
    from django.db import models
    add_interactions_for_all_users()
