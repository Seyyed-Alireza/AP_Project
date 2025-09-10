import pandas as pd
import numpy as np
from django.contrib.auth.models import User
from django.db.models import F
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Product, Comment
import math

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using fallback similarity calculation.")


class RecommendationEngine:
    """
    Simple Recommendation Engine with ICBF and UBCF algorithms
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.interaction_weights = {
            'view': 1.0,
            'like': 2.0,
            'wishlist': 3.0,
            'cart': 4.0,
            'purchase': 5.0
        }
    
    def create_user_item_matrix(self):
        """
        Creates user-item interaction matrix from purchase and interaction history
        """
        # Get all users and products
        users = User.objects.all()
        products = Product.objects.all()
        
        # Create empty matrix
        user_ids = [u.id for u in users]
        product_ids = [p.id for p in products]
        
        matrix = pd.DataFrame(0.0, index=user_ids, columns=product_ids)
        
        # Fill with purchase data (highest weight)
        purchases = ProductPurchaseHistory.objects.all()
        for purchase in purchases:
            matrix.loc[purchase.user.id, purchase.product.id] += purchase.purchase_count * 5.0
        
        # Fill with interaction data
        interactions = ProductSearchHistory.objects.all()
        for interaction in interactions:
            weight = self.interaction_weights.get(interaction.interaction_type, 1.0)
            matrix.loc[interaction.user.id, interaction.product.id] += weight
        
        # Fill with ratings from comments
        comments = Comment.objects.all()
        for comment in comments:
            matrix.loc[comment.user.id, comment.product.id] += comment.rating
        
        self.user_item_matrix = matrix
        return matrix
    
    def calculate_user_similarity(self):
        """
        Calculate user-user similarity matrix using cosine similarity
        """
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
        
        if SKLEARN_AVAILABLE:
            # Use sklearn for efficient cosine similarity calculation
            user_similarity = cosine_similarity(self.user_item_matrix.fillna(0))
        else:
            # Manual cosine similarity calculation
            matrix = self.user_item_matrix.fillna(0)
            user_similarity = self._manual_cosine_similarity(matrix)
        
        self.user_similarity_matrix = pd.DataFrame(
            user_similarity,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
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
        
        if SKLEARN_AVAILABLE:
            # Use sklearn for efficient cosine similarity calculation
            item_similarity = cosine_similarity(item_user_matrix)
        else:
            # Manual cosine similarity calculation
            item_similarity = self._manual_cosine_similarity(item_user_matrix)
        
        self.item_similarity_matrix = pd.DataFrame(
            item_similarity,
            index=item_user_matrix.index,
            columns=item_user_matrix.index
        )
        
        return self.item_similarity_matrix
    
    def _manual_cosine_similarity(self, matrix):
        """
        Manual implementation of cosine similarity for when sklearn is not available
        """
        matrix_values = matrix.values
        norms = np.linalg.norm(matrix_values, axis=1)
        norms = norms.reshape(-1, 1)
        
        # Avoid division by zero
        norms[norms == 0] = 1
        
        normalized_matrix = matrix_values / norms
        similarity = np.dot(normalized_matrix, normalized_matrix.T)
        
        return similarity
    
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
            return [(product_id, recommendation_details.get(product_id, "")) 
                   for product_id, score in sorted_recommendations[:n_recommendations]]
        else:
            return [product_id for product_id, score in sorted_recommendations[:n_recommendations]]
    
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
            return [(product_id, recommendation_details.get(product_id, "")) 
                   for product_id, score in sorted_recommendations[:n_recommendations]]
        else:
            return [product_id for product_id, score in sorted_recommendations[:n_recommendations]]
    
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
        
        return [product.id for product in popular_products]
    
    def _get_popular_products_with_reasons(self, n_recommendations=10, reason="محصولات محبوب"):
        """
        Fallback: Return popular products with reasons for new users
        """
        popular_products = Product.objects.annotate(
            popularity_score=F('sales_count') + F('rating') * 10
        ).order_by('-popularity_score')[:n_recommendations]
        
        return [(product.id, f"{reason} | امتیاز: {product.rating:.1f} | فروش: {product.sales_count}") 
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
