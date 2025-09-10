import pandas as pd
import numpy as np
from django.contrib.auth.models import User
from django.db.models import F
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Product, Comment
import math
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationEngine:
    """
    Simple Recommendation Engine with ICBF and UBCF algorithms
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.matrix_last_updated = None
        self.cache_duration_minutes = 30  # Cache for 30 minutes
        self.interaction_weights = {
            'view': 1.0,
            'like': 2.0,
            'wishlist': 3.0,
            'cart': 4.0,
            'purchase': 5.0,
            'comment': 3.0  # Base weight for comments (multiplied by rating)
        }
    
    def create_user_item_matrix(self, force_rebuild=False):
        """
        Creates user-item interaction matrix from purchase and interaction history
        Only includes users who have interactions to optimize performance
        
        Args:
            force_rebuild (bool): Force rebuild even if cache is valid
        """
        from datetime import datetime, timedelta
        
        # Check if we need to rebuild the matrix
        if not force_rebuild and self.user_item_matrix is not None and self.matrix_last_updated:
            cache_valid_until = self.matrix_last_updated + timedelta(minutes=self.cache_duration_minutes)
            if datetime.now() < cache_valid_until:
                print(f"[INFO] Using cached matrix (updated {self.matrix_last_updated})")
                return self.user_item_matrix
        
        print(f"[INFO] Rebuilding user-item matrix...")
        start_time = datetime.now()
        
        # Get users who have interactions, purchases, or comments
        interacting_users = set()
        
        # Add users from interactions
        for user_id in ProductSearchHistory.objects.values_list('user_id', flat=True).distinct():
            interacting_users.add(user_id)
        
        # Add users from purchases  
        for user_id in ProductPurchaseHistory.objects.values_list('user_id', flat=True).distinct():
            interacting_users.add(user_id)
            
        # Add users from comments
        for user_id in Comment.objects.values_list('user_id', flat=True).distinct():
            interacting_users.add(user_id)
        
        # Get all products that have interactions
        interacted_products = set()
        for product_id in ProductSearchHistory.objects.values_list('product_id', flat=True).distinct():
            interacted_products.add(product_id)
        for product_id in ProductPurchaseHistory.objects.values_list('product_id', flat=True).distinct():
            interacted_products.add(product_id)
        for product_id in Comment.objects.values_list('product_id', flat=True).distinct():
            interacted_products.add(product_id)
        
        user_ids = sorted(list(interacting_users))
        product_ids = sorted(list(interacted_products))
        
        # Create empty matrix
        matrix = pd.DataFrame(0.0, index=user_ids, columns=product_ids)
        
        # Fill with purchase data (highest weight)
        purchases = ProductPurchaseHistory.objects.all()
        for purchase in purchases:
            if purchase.user.id in user_ids and purchase.product.id in product_ids:
                matrix.loc[purchase.user.id, purchase.product.id] += purchase.purchase_count * 5.0
        
        # Fill with interaction data
        interactions = ProductSearchHistory.objects.all()
        for interaction in interactions:
            if interaction.user.id in user_ids and interaction.product.id in product_ids:
                weight = self.interaction_weights.get(interaction.interaction_type, 1.0)
                matrix.loc[interaction.user.id, interaction.product.id] += weight
        
        # Fill with ratings from comments (weighted by rating value)
        comments = Comment.objects.all()
        for comment in comments:
            if comment.user.id in user_ids and comment.product.id in product_ids:
                # Weight comments by rating: higher ratings = stronger preference
                comment_weight = self.interaction_weights['comment'] * (comment.rating / 5.0)
                matrix.loc[comment.user.id, comment.product.id] += comment_weight
        
        # Update cache timestamp
        self.matrix_last_updated = datetime.now()
        self.user_item_matrix = matrix
        
        build_time = (datetime.now() - start_time).total_seconds()
        print(f"[INFO] Matrix rebuilt in {build_time:.2f} seconds. Shape: {matrix.shape}")
        print(f"[INFO] Cache valid until: {self.matrix_last_updated + timedelta(minutes=self.cache_duration_minutes)}")
        
        return matrix
    
    def calculate_user_similarity(self):
        """
        Calculate user-user similarity matrix using cosine similarity
        """
        if self.user_item_matrix is None:
            self.create_user_item_matrix()

        # Filter out users with no interactions (all zeros)
        user_interaction_counts = (self.user_item_matrix != 0).sum(axis=1)
        users_with_interactions = user_interaction_counts[user_interaction_counts > 0].index
        filtered_matrix = self.user_item_matrix.loc[users_with_interactions].fillna(0)
        
        print(f"[DEBUG] User matrix shape: {self.user_item_matrix.shape}")
        print(f"[DEBUG] Filtered to {len(users_with_interactions)} users with interactions")
        print(f"[DEBUG] Filtered user matrix shape: {filtered_matrix.shape}")
        
        # Use sklearn for efficient cosine similarity calculation
        user_similarity = cosine_similarity(filtered_matrix)
        print(f"[DEBUG] User similarity unique values: {np.unique(user_similarity.flatten())[:10]}")
        
        self.user_similarity_matrix = pd.DataFrame(
            user_similarity,
            index=filtered_matrix.index,
            columns=filtered_matrix.index
        )
        
        return self.user_similarity_matrix
    
    def calculate_item_similarity(self):
        """
        Calculate item-item similarity matrix using cosine similarity
        """
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
        
        # Transpose to get item-user matrix
        item_user_matrix = self.user_item_matrix.T.fillna(0)
        
        print(f"[DEBUG] Item-user matrix shape: {item_user_matrix.shape}")
        print(f"[DEBUG] Matrix non-zero count: {(item_user_matrix != 0).sum().sum()}")
        
        # Filter out items with very few interactions (less than 2 users)
        item_interaction_counts = (item_user_matrix != 0).sum(axis=1)
        items_with_sufficient_interactions = item_interaction_counts[item_interaction_counts >= 2].index
        
        if len(items_with_sufficient_interactions) < 2:
            # If we don't have enough items with sufficient interactions, use all items
            print("[DEBUG] Not enough items with 2+ interactions, using all items")
            filtered_matrix = item_user_matrix
        else:
            filtered_matrix = item_user_matrix.loc[items_with_sufficient_interactions]
            print(f"[DEBUG] Filtered to {len(items_with_sufficient_interactions)} items with 2+ interactions")
        
        print(f"[DEBUG] Final matrix shape: {filtered_matrix.shape}")
        
        # Use sklearn for efficient cosine similarity calculation
        item_similarity = cosine_similarity(filtered_matrix)
        print(f"[DEBUG] Item similarity unique values: {len(np.unique(item_similarity.flatten()))} unique values")
        print(f"[DEBUG] Similarity range: {item_similarity.min():.3f} to {item_similarity.max():.3f}")
        
        # Create similarity matrix with filtered items
        self.item_similarity_matrix = pd.DataFrame(
            item_similarity,
            index=filtered_matrix.index,
            columns=filtered_matrix.index
        )
        
        return self.item_similarity_matrix
    
    def user_based_collaborative_filtering(self, user_id, n_recommendations=10, include_reasons=False):
        """
        UBCF: Recommend products based on similar users' preferences
        Returns predicted ratings and reasons
        """
        if self.user_similarity_matrix is None:
            self.calculate_user_similarity()
        
        if user_id not in self.user_similarity_matrix.index:
            if include_reasons:
                return self._get_popular_products_with_reasons(n_recommendations, "محصولات محبوب - کاربر جدید")
            return self._get_popular_products(n_recommendations)
        
        # Get similar users (excluding the user themselves)
        similar_users = self.user_similarity_matrix[user_id].sort_values(ascending=False)[1:11]
        
        # Filter out users with very low similarity
        similar_users = similar_users[similar_users > 0.1]
        
        if len(similar_users) == 0:
            if include_reasons:
                return self._get_popular_products_with_reasons(n_recommendations, "محصولات محبوب - عدم شباهت کافی")
            return self._get_popular_products(n_recommendations)
        
        # Get products that similar users liked but current user hasn't interacted with
        user_products = self.user_item_matrix.loc[user_id]
        unrated_products = user_products[user_products == 0].index
        
        recommendations = {}
        recommendation_details = {}
        
        for product_id in unrated_products:
            weighted_sum = 0
            similarity_sum = 0
            contributing_users = []
            
            for similar_user_id, similarity in similar_users.items():
                user_rating = self.user_item_matrix.loc[similar_user_id, product_id]
                if user_rating > 0:
                    weighted_sum += similarity * user_rating
                    similarity_sum += abs(similarity)
                    contributing_users.append((similar_user_id, similarity, user_rating))
            
            if similarity_sum > 0:
                predicted_rating = weighted_sum / similarity_sum
                recommendations[product_id] = predicted_rating
                
                # Create detailed reason
                top_users = sorted(contributing_users, key=lambda x: x[1], reverse=True)[:3]
                user_count = len(contributing_users)
                avg_similarity = sum(u[1] for u in contributing_users) / len(contributing_users)
                
                reason = f"امتیاز پیش‌بینی: {predicted_rating:.2f} | بر اساس {user_count} کاربر مشابه | میانگین شباهت: {avg_similarity:.2f}"
                recommendation_details[product_id] = reason
        
        # Sort and return top N recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        if include_reasons:
            result = []
            for product_id, predicted_rating in sorted_recommendations[:n_recommendations]:
                try:
                    product = Product.objects.get(id=product_id)
                    result.append({
                        'product': product,
                        'reason': recommendation_details.get(product_id, ""),
                        'predicted_rating': round(predicted_rating, 2)
                    })
                except Product.DoesNotExist:
                    continue
            return result
        else:
            result = []
            for product_id, predicted_rating in sorted_recommendations[:n_recommendations]:
                try:
                    product = Product.objects.get(id=product_id)
                    result.append({
                        'product': product,
                        'predicted_rating': round(predicted_rating, 2)
                    })
                except Product.DoesNotExist:
                    continue
            return result
    
    def item_based_collaborative_filtering(self, user_id, n_recommendations=10, include_reasons=False):
        """
        IBCF: Recommend products based on item similarity
        Returns predicted ratings and reasons
        """
        if self.item_similarity_matrix is None:
            self.calculate_item_similarity()
        
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
        
        if user_id not in self.user_item_matrix.index:
            if include_reasons:
                return self._get_popular_products_with_reasons(n_recommendations, "محصولات محبوب - کاربر جدید")
            return self._get_popular_products(n_recommendations)
        
        # Get user's rated products
        user_products = self.user_item_matrix.loc[user_id]
        rated_products = user_products[user_products > 0]
        
        if len(rated_products) == 0:
            if include_reasons:
                return self._get_popular_products_with_reasons(n_recommendations, "محصولات محبوب - عدم تعامل قبلی")
            return self._get_popular_products(n_recommendations)
        
        recommendations = {}
        recommendation_details = {}
        
        # For each unrated product, calculate similarity to user's rated products
        unrated_products = user_products[user_products == 0].index
        
        for product_id in unrated_products:
            if product_id not in self.item_similarity_matrix.index:
                continue
                
            weighted_sum = 0
            similarity_sum = 0
            similar_items = []
            
            for rated_product_id, user_rating in rated_products.items():
                if rated_product_id in self.item_similarity_matrix.columns:
                    similarity = self.item_similarity_matrix.loc[product_id, rated_product_id]
                    if similarity > 0.1:  # Only consider meaningful similarities
                        weighted_sum += similarity * user_rating
                        similarity_sum += abs(similarity)
                        similar_items.append((rated_product_id, similarity, user_rating))
            
            if similarity_sum > 0:
                predicted_rating = weighted_sum / similarity_sum
                recommendations[product_id] = predicted_rating
                
                # Create detailed reason
                top_similar = sorted(similar_items, key=lambda x: x[1], reverse=True)[:3]
                item_count = len(similar_items)
                avg_similarity = sum(item[1] for item in similar_items) / len(similar_items)
                
                try:
                    # Get names of most similar products
                    similar_names = []
                    for pid, sim, rating in top_similar[:2]:
                        try:
                            product = Product.objects.get(id=pid)
                            similar_names.append(f"{product.name[:20]}...")
                        except Product.DoesNotExist:
                            pass
                    
                    if similar_names:
                        reason = f"امتیاز پیش‌بینی: {predicted_rating:.2f} | مشابه به: {', '.join(similar_names)} | میانگین شباهت: {avg_similarity:.2f}"
                    else:
                        reason = f"امتیاز پیش‌بینی: {predicted_rating:.2f} | بر اساس {item_count} محصول مشابه | میانگین شباهت: {avg_similarity:.2f}"
                except:
                    reason = f"امتیاز پیش‌بینی: {predicted_rating:.2f} | بر اساس {item_count} محصول مشابه | میانگین شباهت: {avg_similarity:.2f}"
                
                recommendation_details[product_id] = reason
        
        # Sort and return top N recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        if include_reasons:
            result = []
            for product_id, predicted_rating in sorted_recommendations[:n_recommendations]:
                try:
                    product = Product.objects.get(id=product_id)
                    result.append({
                        'product': product,
                        'reason': recommendation_details.get(product_id, ""),
                        'predicted_rating': round(predicted_rating, 2)
                    })
                except Product.DoesNotExist:
                    continue
            return result
        else:
            result = []
            for product_id, predicted_rating in sorted_recommendations[:n_recommendations]:
                try:
                    product = Product.objects.get(id=product_id)
                    result.append({
                        'product': product,
                        'predicted_rating': round(predicted_rating, 2)
                    })
                except Product.DoesNotExist:
                    continue
            return result
    
    def predict_rating(self, user_id, product_id, method='both'):
        """
        Predict rating for a specific user-product pair
        """
        if method == 'ubcf' or method == 'both':
            ubcf_rating = self._predict_rating_ubcf(user_id, product_id)
        else:
            ubcf_rating = None
            
        if method == 'ibcf' or method == 'both':
            ibcf_rating = self._predict_rating_ibcf(user_id, product_id)
        else:
            ibcf_rating = None
        
        if method == 'both':
            if ubcf_rating is not None and ibcf_rating is not None:
                # Average of both methods
                return (ubcf_rating + ibcf_rating) / 2
            elif ubcf_rating is not None:
                return ubcf_rating
            elif ibcf_rating is not None:
                return ibcf_rating
            else:
                return None
        elif method == 'ubcf':
            return ubcf_rating
        elif method == 'ibcf':
            return ibcf_rating
        else:
            return None
    
    def _predict_rating_ubcf(self, user_id, product_id):
        """Predict rating using User-based CF"""
        if self.user_similarity_matrix is None:
            self.calculate_user_similarity()
        
        if user_id not in self.user_similarity_matrix.index:
            return None
        
        similar_users = self.user_similarity_matrix[user_id].sort_values(ascending=False)[1:11]
        similar_users = similar_users[similar_users > 0.1]
        
        weighted_sum = 0
        similarity_sum = 0
        
        for similar_user_id, similarity in similar_users.items():
            if product_id in self.user_item_matrix.columns:
                user_rating = self.user_item_matrix.loc[similar_user_id, product_id]
                if user_rating > 0:
                    weighted_sum += similarity * user_rating
                    similarity_sum += abs(similarity)
        
        if similarity_sum > 0:
            return weighted_sum / similarity_sum
        return None
    
    def _predict_rating_ibcf(self, user_id, product_id):
        """Predict rating using Item-based CF"""
        if self.item_similarity_matrix is None:
            self.calculate_item_similarity()
        
        if user_id not in self.user_item_matrix.index or product_id not in self.item_similarity_matrix.index:
            return None
        
        user_products = self.user_item_matrix.loc[user_id]
        rated_products = user_products[user_products > 0]
        
        weighted_sum = 0
        similarity_sum = 0
        
        for rated_product_id, user_rating in rated_products.items():
            if rated_product_id in self.item_similarity_matrix.columns:
                similarity = self.item_similarity_matrix.loc[product_id, rated_product_id]
                if similarity > 0.1:
                    weighted_sum += similarity * user_rating
                    similarity_sum += abs(similarity)
        
        if similarity_sum > 0:
            return weighted_sum / similarity_sum
        return None
    
    def _get_popular_products(self, n_recommendations=10):
        """
        Fallback: Return popular products for new users
        """
        popular_products = Product.objects.annotate(
            popularity_score=F('sales_count') + F('rating') * 10
        ).order_by('-popularity_score')[:n_recommendations]
        
        return [{'product': product, 'predicted_rating': product.rating} for product in popular_products]
    
    def _get_popular_products_with_reasons(self, n_recommendations=10, reason="محصولات محبوب"):
        """
        Fallback: Return popular products with reasons for new users
        """
        popular_products = Product.objects.annotate(
            popularity_score=F('sales_count') + F('rating') * 10
        ).order_by('-popularity_score')[:n_recommendations]
        
        return [{'product': product, 
                'reason': f"{reason} | امتیاز: {product.rating:.1f} | فروش: {product.sales_count}",
                'predicted_rating': product.rating} 
               for product in popular_products]
    
    def get_similarity_matrices(self):
        """
        Get both similarity matrices for analysis
        """
        if self.user_similarity_matrix is None:
            self.calculate_user_similarity()
        
        if self.item_similarity_matrix is None:
            self.calculate_item_similarity()
        
        return {
            'user_similarity': self.user_similarity_matrix,
            'item_similarity': self.item_similarity_matrix,
            'user_item_matrix': self.user_item_matrix
        }
    
    def get_cache_status(self):
        """
        Get information about the matrix cache status
        """
        from datetime import datetime, timedelta
        
        if self.matrix_last_updated is None:
            return {
                'cached': False,
                'last_updated': None,
                'cache_valid': False,
                'expires_in': None,
                'cache_duration_minutes': self.cache_duration_minutes
            }
        
        cache_valid_until = self.matrix_last_updated + timedelta(minutes=self.cache_duration_minutes)
        now = datetime.now()
        cache_valid = now < cache_valid_until
        
        if cache_valid:
            expires_in = (cache_valid_until - now).total_seconds() / 60  # minutes
        else:
            expires_in = 0
        
        return {
            'cached': True,
            'last_updated': self.matrix_last_updated,
            'cache_valid': cache_valid,
            'expires_in_minutes': round(expires_in, 1),
            'cache_duration_minutes': self.cache_duration_minutes,
            'matrix_shape': self.user_item_matrix.shape if self.user_item_matrix is not None else None
        }
    
    def force_matrix_update(self):
        """
        Force an immediate update of the user-item matrix
        Useful when you know new data has been added and want fresh recommendations
        """
        print("[INFO] Forcing matrix update...")
        # Clear similarity matrices as they need to be recalculated
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        return self.create_user_item_matrix(force_rebuild=True)
    
    def set_cache_duration(self, minutes):
        """
        Set how long the matrix should be cached
        
        Args:
            minutes (int): Cache duration in minutes
        """
        self.cache_duration_minutes = minutes
        print(f"[INFO] Cache duration set to {minutes} minutes")
    
    def is_user_in_matrix(self, user_id):
        """
        Check if a specific user is included in the current matrix
        
        Args:
            user_id (int): User ID to check
            
        Returns:
            bool: True if user is in matrix, False otherwise
        """
        if self.user_item_matrix is None:
            return False
        return user_id in self.user_item_matrix.index


