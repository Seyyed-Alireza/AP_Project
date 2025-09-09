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

def add_interactions_for_user(username):
    """Add sample interactions for a specific user"""
    try:
        user = User.objects.get(username=username)
        print(f"Adding interactions for user: {user.username} (ID: {user.id})")
        
        # Get some random products
        products = list(Product.objects.all()[:20])
        
        # Add search history
        for i in range(15):
            product = random.choice(products)
            ProductSearchHistory.objects.create(
                user=user,
                product=product,
                interaction_type=random.choice(['view', 'like', 'cart']),
                searched_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
        
        # Add purchase history
        for i in range(3):
            product = random.choice(products)
            ProductPurchaseHistory.objects.create(
                user=user,
                product=product,
                rating=random.uniform(3.0, 5.0),
                purchased_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
        
        # Add comments
        for i in range(2):
            product = random.choice(products)
            Comment.objects.create(
                user=user,
                product=product,
                content=f"Great product! Rating: {random.uniform(3.0, 5.0):.1f}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
        
        print(f"✅ Added 15 searches, 3 purchases, and 2 comments for {user.username}")
        return True
        
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return False

def main():
    print("=== ADD INTERACTIONS FOR USER ===")
    
    # Show all users
    print("\nAvailable users:")
    for user in User.objects.all().order_by('id'):
        search_count = ProductSearchHistory.objects.filter(user=user).count()
        if search_count > 0:
            print(f"  {user.username} (ID: {user.id}) - {search_count} searches ✅")
        else:
            print(f"  {user.username} (ID: {user.id}) - No interactions ❌")
    
    # You can modify this to add interactions for your current user
    # Replace 'your_username' with the actual username you're logged in as
    print(f"\nTo fix recommendations, tell me which username you're logged in as,")
    print(f"or manually edit this script and change 'your_username' below:")
    
    # Uncomment and modify this line with your actual username:
    # add_interactions_for_user('your_username')
    
    # For testing, let's add data for a few common usernames:
    common_usernames = ['test', 'user', 'demo', 'guest']
    for username in common_usernames:
        try:
            if User.objects.filter(username=username).exists():
                add_interactions_for_user(username)
        except:
            pass

if __name__ == "__main__":
    main()
