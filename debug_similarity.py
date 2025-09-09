#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Comment, Product
from django.contrib.auth.models import User
from recommendations.engine import RecommendationEngine
import pandas as pd
import numpy as np

def debug_similarity():
    print("=== DEBUGGING SIMILARITY CALCULATION ===")
    
    # Check data counts
    print(f"Users: {User.objects.count()}")
    print(f"Products: {Product.objects.count()}")
    print(f"Search interactions: {ProductSearchHistory.objects.count()}")
    print(f"Purchase interactions: {ProductPurchaseHistory.objects.count()}")
    print(f"Comments: {Comment.objects.count()}")
    
    # Check some actual interactions
    print("\n=== SAMPLE INTERACTIONS ===")
    search_sample = ProductSearchHistory.objects.all()[:5]
    for search in search_sample:
        print(f"User {search.user.id} searched product {search.product.id}")
    
    purchase_sample = ProductPurchaseHistory.objects.all()[:5]
    for purchase in purchase_sample:
        print(f"User {purchase.user.id} purchased product {purchase.product.id}")
    
    comment_sample = Comment.objects.all()[:5]
    for comment in comment_sample:
        print(f"User {comment.user.id} rated product {comment.product.id} with {comment.rating}")
    
    # Test the engine
    print("\n=== TESTING ENGINE ===")
    engine = RecommendationEngine()
    
    # Check user-item matrix
    user_item_matrix = engine.create_user_item_matrix()
    print(f"User-item matrix shape: {user_item_matrix.shape}")
    print(f"Non-zero values: {(user_item_matrix != 0).sum().sum()}")
    print(f"Matrix sample:\n{user_item_matrix.iloc[:5, :5]}")
    
    # Check unique values in the matrix
    unique_values = user_item_matrix.values.flatten()
    unique_values = unique_values[~np.isnan(unique_values)]
    print(f"Unique values in matrix: {np.unique(unique_values)}")
    
    # Check item similarity calculation
    print("\n=== ITEM SIMILARITY DEBUG ===")
    item_similarity = engine.calculate_item_similarity()
    print(f"Item similarity matrix shape: {item_similarity.shape}")
    
if __name__ == "__main__":
    debug_similarity()
