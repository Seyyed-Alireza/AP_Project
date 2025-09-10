#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkincareRecommendationPlatform.settings')
django.setup()

from recommendations.engine import RecommendationEngine
from django.contrib.auth.models import User
from mainpage.models import Product
import pandas as pd

def display_user_item_matrix():
    """Display the user-item matrix in terminal"""
    print("=== USER-ITEM MATRIX DISPLAY ===")
    
    # Create recommendation engine
    engine = RecommendationEngine()
    
    print("🔄 Creating user-item matrix...")
    matrix = engine.create_user_item_matrix()
    
    if matrix is not None:
        print(f"✅ Matrix created successfully!")
        print(f"📊 Matrix shape: {matrix.shape}")
        print(f"   Users: {matrix.shape[0]}")
        print(f"   Products: {matrix.shape[1]}")
        
        # Display matrix statistics
        print(f"\n📈 Matrix Statistics:")
        print(f"   Total cells: {matrix.size:,}")
        print(f"   Non-zero cells: {(matrix > 0).sum().sum():,}")
        print(f"   Sparsity: {((matrix == 0).sum().sum() / matrix.size * 100):.1f}%")
        print(f"   Max value: {matrix.max().max():.2f}")
        print(f"   Min value: {matrix.min().min():.2f}")
        print(f"   Mean value: {matrix.mean().mean():.2f}")
        
        # Display a sample of the matrix (first 10 users and products)
        print(f"\n🔍 Sample Matrix (First 10 users × 10 products):")
        print("=" * 80)
        
        # Get sample data
        sample_matrix = matrix.iloc[:10, :10]
        
        # Get user and product names for better display
        user_names = []
        for user_id in sample_matrix.index[:10]:
            try:
                user = User.objects.get(id=user_id)
                user_names.append(f"User_{user.id}({user.username[:8]})")
            except User.DoesNotExist:
                user_names.append(f"User_{user_id}")
        
        product_names = []
        for product_id in sample_matrix.columns[:10]:
            try:
                product = Product.objects.get(id=product_id)
                product_names.append(f"Prod_{product.id}({product.name[:10]})")
            except Product.DoesNotExist:
                product_names.append(f"Prod_{product_id}")
        
        # Create a formatted display matrix
        display_df = pd.DataFrame(
            sample_matrix.values,
            index=user_names,
            columns=product_names
        )
        
        # Display with formatting
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.float_format', '{:.1f}'.format)
        
        print(display_df)
        
        # Show specific user interactions
        print(f"\n👤 Detailed View - First User Interactions:")
        print("=" * 60)
        first_user_id = matrix.index[0]
        first_user_row = matrix.iloc[0]
        non_zero_interactions = first_user_row[first_user_row > 0]
        
        try:
            first_user = User.objects.get(id=first_user_id)
            print(f"User: {first_user.username} (ID: {first_user_id})")
        except User.DoesNotExist:
            print(f"User ID: {first_user_id}")
        
        print(f"Total interactions: {len(non_zero_interactions)}")
        print(f"Interaction values:")
        
        for product_id, value in non_zero_interactions.head(10).items():
            try:
                product = Product.objects.get(id=product_id)
                print(f"  {product.name[:30]:<30} | Value: {value:.2f}")
            except Product.DoesNotExist:
                print(f"  Product ID {product_id:<20} | Value: {value:.2f}")
        
        if len(non_zero_interactions) > 10:
            print(f"  ... and {len(non_zero_interactions) - 10} more interactions")
        
        # Show matrix density by user
        print(f"\n📊 User Activity Summary (Top 10 most active users):")
        print("=" * 60)
        user_activity = (matrix > 0).sum(axis=1).sort_values(ascending=False)
        
        for i, (user_id, interaction_count) in enumerate(user_activity.head(10).items()):
            try:
                user = User.objects.get(id=user_id)
                username = user.username
            except User.DoesNotExist:
                username = f"User_{user_id}"
            
            print(f"  {i+1:2}. {username:<15} | {interaction_count:3} products | {(interaction_count/matrix.shape[1]*100):5.1f}% coverage")
        
        print(f"\n✅ Matrix analysis complete!")
        
    else:
        print("❌ Failed to create matrix!")
    
    return matrix

if __name__ == "__main__":
    matrix = display_user_item_matrix()
