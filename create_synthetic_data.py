#!/usr/bin/env python
import os
import sys
import django
import random
import numpy as np

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Comment, Product
from django.contrib.auth.models import User
from django.utils import timezone

def create_synthetic_data():
    """
    Create synthetic user interactions to demonstrate diverse similarity patterns
    """
    print("=== CREATING SYNTHETIC TEST DATA ===")
    
    # Get available users and products
    users = list(User.objects.all()[:20])  # Use first 20 users
    products = list(Product.objects.all()[:50])  # Use first 50 products
    
    print(f"Using {len(users)} users and {len(products)} products")
    
    # Clear existing test data (keep original data)
    print("Clearing existing synthetic data...")
    ProductSearchHistory.objects.filter(user__in=users, product__in=products).delete()
    ProductPurchaseHistory.objects.filter(user__in=users, product__in=products).delete()
    Comment.objects.filter(user__in=users, product__in=products).delete()
    
    # Create user groups with different preferences
    user_groups = {
        'skincare_enthusiasts': users[:5],    # Love high-end skincare
        'budget_conscious': users[5:10],       # Prefer affordable products
        'anti_aging_focused': users[10:15],    # Focus on anti-aging
        'sensitive_skin': users[15:20],        # Sensitive skin products
    }
    
    product_groups = {
        'premium': products[:12],      # High-end products
        'budget': products[12:25],     # Budget products
        'anti_aging': products[25:37], # Anti-aging products
        'sensitive': products[37:50],  # Sensitive skin products
    }
    
    interactions_created = 0
    
    # Create group-based interactions
    for group_name, group_users in user_groups.items():
        print(f"Creating interactions for {group_name} group...")
        
        if group_name == 'skincare_enthusiasts':
            preferred_products = product_groups['premium'] + product_groups['anti_aging'][:6]
        elif group_name == 'budget_conscious':
            preferred_products = product_groups['budget'] + product_groups['sensitive'][:6]
        elif group_name == 'anti_aging_focused':
            preferred_products = product_groups['anti_aging'] + product_groups['premium'][:6]
        else:  # sensitive_skin
            preferred_products = product_groups['sensitive'] + product_groups['budget'][:6]
        
        for user in group_users:
            # Each user interacts with 8-15 products from their preferred group
            num_interactions = random.randint(8, 15)
            selected_products = random.sample(preferred_products, min(num_interactions, len(preferred_products)))
            
            for product in selected_products:
                # Create search history (higher weight)
                search_count = random.randint(1, 5)
                for _ in range(search_count):
                    ProductSearchHistory.objects.create(
                        user=user,
                        product=product,
                        interaction_type='view'
                    )
                    interactions_created += 1
                
                # 30% chance of purchase
                if random.random() < 0.3:
                    ProductPurchaseHistory.objects.create(
                        user=user,
                        product=product,
                        purchase_count=random.randint(1, 3)
                    )
                    interactions_created += 1
                
                # 40% chance of rating/comment
                if random.random() < 0.4:
                    # Rating based on group preference
                    if product in preferred_products:
                        rating = random.randint(4, 5)  # High rating for preferred products
                    else:
                        rating = random.randint(2, 4)  # Mixed ratings for others
                    
                    Comment.objects.create(
                        user=user,
                        product=product,
                        rating=rating,
                        text=f"Test comment by {user.username}"
                    )
                    interactions_created += 1
    
    # Add some cross-group interactions for realism
    print("Adding cross-group interactions...")
    all_users = users
    all_products = products
    
    for _ in range(50):  # 50 random cross-group interactions
        user = random.choice(all_users)
        product = random.choice(all_products)
        
        # Random search
        ProductSearchHistory.objects.create(
            user=user,
            product=product,
            interaction_type='view'
        )
        interactions_created += 1
        
        # Random rating (lower probability)
        if random.random() < 0.2:
            Comment.objects.create(
                user=user,
                product=product,
                rating=random.randint(1, 5),
                text=f"Random interaction by {user.username}"
            )
            interactions_created += 1
    
    print(f"Created {interactions_created} synthetic interactions!")
    
    # Print summary
    print("\n=== DATA SUMMARY ===")
    print(f"Total search interactions: {ProductSearchHistory.objects.count()}")
    print(f"Total purchase interactions: {ProductPurchaseHistory.objects.count()}")
    print(f"Total comments/ratings: {Comment.objects.count()}")
    
    print("\n=== USER GROUP INTERACTIONS ===")
    for group_name, group_users in user_groups.items():
        user_ids = [u.id for u in group_users]
        searches = ProductSearchHistory.objects.filter(user_id__in=user_ids).count()
        purchases = ProductPurchaseHistory.objects.filter(user_id__in=user_ids).count()
        comments = Comment.objects.filter(user_id__in=user_ids).count()
        print(f"{group_name}: {searches} searches, {purchases} purchases, {comments} comments")

if __name__ == "__main__":
    create_synthetic_data()
