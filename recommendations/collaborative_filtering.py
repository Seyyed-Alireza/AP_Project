import pandas as pd
import numpy as np
from django.contrib.auth.models import User
from mainpage.models import Product, Comment
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
import math
from django.db.models import Avg, Count

try:
    from scipy.stats import pearsonr
    from sklearn.metrics.pairwise import cosine_similarity
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class CollaborativeFilteringEngine:
    """
    Traditional Collaborative Filtering with User-Based and Item-Based approaches
    Creates similarity matrices and provides rating predictions
    """
    
    def __init__(self, debug=False):
        self.debug = debug
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.mean_user_ratings = None
        self.mean_item_ratings = None
        self.global_mean = None
        
        # Interaction weights for converting interactions to ratings
        self.interaction_weights = {
            'view': 1.0,
            'like': 3.0,
            'wishlist': 4.0,
            'cart': 4.5,
            'purchase': 5.0
        }
    
    def log(self, message):
        """Debug logging"""
        if self.debug:
            print(f"[CF_Engine] {message}")
    
    def create_user_item_matrix(self):
        """
        Create user-item rating matrix from interaction data
        """
        self.log("Creating user-item matrix...")
        
        # Get all users and products
        users = User.objects.all().values_list('id', flat=True)
        products = Product.objects.all().values_list('id', flat=True)
        
        # Initialize matrix with zeros
        user_item_data = []
        
        # Process explicit ratings from comments
        self.log("Processing explicit ratings from comments...")
        comments = Comment.objects.select_related('user', 'product').all()
        rating_dict = {}
        
        for comment in comments:
            user_id = comment.user.id
            product_id = comment.product.id
            rating = float(comment.rating)
            
            key = (user_id, product_id)
            if key not in rating_dict or rating_dict[key] < rating:
                rating_dict[key] = rating
        
        # Process implicit ratings from interactions
        self.log("Processing implicit ratings from interactions...")
        interactions = ProductSearchHistory.objects.select_related('user', 'product').all()
        
        for interaction in interactions:
            user_id = interaction.user.id
            product_id = interaction.product.id
            interaction_type = interaction.interaction_type
            
            # Convert interaction to rating
            implicit_rating = self.interaction_weights.get(interaction_type, 1.0)
            
            key = (user_id, product_id)
            if key in rating_dict:
                # Combine explicit and implicit ratings (weighted average)
                rating_dict[key] = (rating_dict[key] * 0.7 + implicit_rating * 0.3)
            else:
                rating_dict[key] = implicit_rating
        
        # Process purchase history with higher weight
        self.log("Processing purchase history...")
        purchases = ProductPurchaseHistory.objects.select_related('user', 'product').all()
        
        for purchase in purchases:
            user_id = purchase.user.id
            product_id = purchase.product.id
            purchase_count = purchase.purchase_count
            
            # Higher rating for multiple purchases
            purchase_rating = min(5.0, 4.0 + (purchase_count - 1) * 0.2)
            
            key = (user_id, product_id)
            if key in rating_dict:
                # Weighted average with purchase data having higher weight
                rating_dict[key] = (rating_dict[key] * 0.4 + purchase_rating * 0.6)
            else:
                rating_dict[key] = purchase_rating
        
        # Create DataFrame
        if rating_dict:
            user_item_data = [(user_id, product_id, rating) 
                            for (user_id, product_id), rating in rating_dict.items()]
            df = pd.DataFrame(user_item_data, columns=['user_id', 'product_id', 'rating'])
            
            # Create pivot table
            self.user_item_matrix = df.pivot_table(
                index='user_id', 
                columns='product_id', 
                values='rating', 
                fill_value=0
            )
        else:
            # Create empty matrix if no data
            self.user_item_matrix = pd.DataFrame(
                index=list(users), 
                columns=list(products)
            ).fillna(0)
        
        # Calculate means
        self.mean_user_ratings = self.user_item_matrix.mean(axis=1)
        self.mean_item_ratings = self.user_item_matrix.mean(axis=0)
        self.global_mean = self.user_item_matrix.values[self.user_item_matrix.values > 0].mean()
        
        self.log(f"Created matrix with shape: {self.user_item_matrix.shape}")
        self.log(f"Global mean rating: {self.global_mean:.2f}")
        return self.user_item_matrix
    
    def calculate_user_similarity(self, method='cosine'):
        """
        Calculate user-user similarity matrix
        """
        self.log(f"Calculating user similarity using {method}...")
        
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
        
        # Get matrix with only users who have ratings
        user_matrix = self.user_item_matrix.copy()
        
        # Remove users with no ratings
        user_matrix = user_matrix.loc[(user_matrix != 0).any(axis=1)]
        
        if method == 'cosine':
            if SCIPY_AVAILABLE:
                # Cosine similarity
                similarity_matrix = cosine_similarity(user_matrix)
                similarity_df = pd.DataFrame(
                    similarity_matrix,
                    index=user_matrix.index,
                    columns=user_matrix.index
                )
            else:
                # Manual cosine similarity calculation
                similarity_df = self._manual_cosine_similarity(user_matrix)
        
        elif method == 'pearson':
            # Pearson correlation using pandas (always available)
            similarity_df = user_matrix.T.corr()
        
        elif method == 'adjusted_cosine':
            # Mean-centered cosine similarity
            user_means = user_matrix.mean(axis=1)
            centered_matrix = user_matrix.sub(user_means, axis=0)
            
            if SCIPY_AVAILABLE:
                similarity_matrix = cosine_similarity(centered_matrix)
                similarity_df = pd.DataFrame(
                    similarity_matrix,
                    index=user_matrix.index,
                    columns=user_matrix.index
                )
            else:
                similarity_df = self._manual_cosine_similarity(centered_matrix)
        
        # Fill NaN values with 0
        similarity_df = similarity_df.fillna(0)
        
        # Set diagonal to 1 (user similarity with themselves)
        np.fill_diagonal(similarity_df.values, 1)
        
        self.user_similarity_matrix = similarity_df
        self.log(f"User similarity matrix shape: {similarity_df.shape}")
        return similarity_df
    
    def calculate_item_similarity(self, method='cosine'):
        """
        Calculate item-item similarity matrix
        """
        self.log(f"Calculating item similarity using {method}...")
        
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
        
        # Transpose to get item-user matrix
        item_matrix = self.user_item_matrix.T.copy()
        
        # Remove items with no ratings
        item_matrix = item_matrix.loc[(item_matrix != 0).any(axis=1)]
        
        if method == 'cosine':
            if SCIPY_AVAILABLE:
                # Cosine similarity
                similarity_matrix = cosine_similarity(item_matrix)
                similarity_df = pd.DataFrame(
                    similarity_matrix,
                    index=item_matrix.index,
                    columns=item_matrix.index
                )
            else:
                similarity_df = self._manual_cosine_similarity(item_matrix)
        
        elif method == 'pearson':
            # Pearson correlation using pandas
            similarity_df = item_matrix.T.corr()
        
        elif method == 'adjusted_cosine':
            # User mean-centered cosine similarity for items
            user_means = self.user_item_matrix.mean(axis=1)
            centered_matrix = self.user_item_matrix.sub(user_means, axis=0)
            item_centered = centered_matrix.T
            
            if SCIPY_AVAILABLE:
                similarity_matrix = cosine_similarity(item_centered)
                similarity_df = pd.DataFrame(
                    similarity_matrix,
                    index=item_matrix.index,
                    columns=item_matrix.index
                )
            else:
                similarity_df = self._manual_cosine_similarity(item_centered)
        
        # Fill NaN values with 0
        similarity_df = similarity_df.fillna(0)
        
        # Set diagonal to 1 (item similarity with themselves)
        np.fill_diagonal(similarity_df.values, 1)
        
        self.item_similarity_matrix = similarity_df
        self.log(f"Item similarity matrix shape: {similarity_df.shape}")
        return similarity_df
    
    def predict_rating_ubcf(self, user_id, item_id, k=50):
        """
        Predict rating using User-Based Collaborative Filtering
        """
        if self.user_similarity_matrix is None:
            self.calculate_user_similarity()
        
        if user_id not in self.user_similarity_matrix.index:
            return self.global_mean if self.global_mean else 3.0
        
        if item_id not in self.user_item_matrix.columns:
            return self.global_mean if self.global_mean else 3.0
        
        # Get similar users
        user_similarities = self.user_similarity_matrix.loc[user_id].drop(user_id)
        
        # Filter users who have rated this item
        rated_users = self.user_item_matrix[item_id]
        rated_users = rated_users[rated_users > 0]
        
        # Get similarities for users who rated this item
        common_users = user_similarities.index.intersection(rated_users.index)
        
        if len(common_users) == 0:
            return self.mean_item_ratings[item_id] if item_id in self.mean_item_ratings else self.global_mean
        
        # Get top k similar users
        similar_users = user_similarities.loc[common_users].nlargest(k)
        
        if len(similar_users) == 0:
            return self.mean_item_ratings[item_id] if item_id in self.mean_item_ratings else self.global_mean
        
        # Calculate weighted average prediction
        user_mean = self.mean_user_ratings[user_id]
        
        numerator = 0
        denominator = 0
        
        for similar_user, similarity in similar_users.items():
            if similarity > 0:  # Only positive similarities
                similar_user_rating = self.user_item_matrix.loc[similar_user, item_id]
                similar_user_mean = self.mean_user_ratings[similar_user]
                
                numerator += similarity * (similar_user_rating - similar_user_mean)
                denominator += abs(similarity)
        
        if denominator == 0:
            prediction = user_mean
        else:
            prediction = user_mean + (numerator / denominator)
        
        # Clamp prediction to valid range
        return max(1.0, min(5.0, prediction))
    
    def predict_rating_ibcf(self, user_id, item_id, k=50):
        """
        Predict rating using Item-Based Collaborative Filtering
        """
        if self.item_similarity_matrix is None:
            self.calculate_item_similarity()
        
        if user_id not in self.user_item_matrix.index:
            return self.global_mean if self.global_mean else 3.0
        
        if item_id not in self.item_similarity_matrix.index:
            return self.global_mean if self.global_mean else 3.0
        
        # Get similar items
        item_similarities = self.item_similarity_matrix.loc[item_id].drop(item_id)
        
        # Get items rated by this user
        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0]
        
        # Get similarities for items rated by this user
        common_items = item_similarities.index.intersection(rated_items.index)
        
        if len(common_items) == 0:
            return self.mean_user_ratings[user_id] if user_id in self.mean_user_ratings else self.global_mean
        
        # Get top k similar items
        similar_items = item_similarities.loc[common_items].nlargest(k)
        
        if len(similar_items) == 0:
            return self.mean_user_ratings[user_id] if user_id in self.mean_user_ratings else self.global_mean
        
        # Calculate weighted average prediction
        numerator = 0
        denominator = 0
        
        for similar_item, similarity in similar_items.items():
            if similarity > 0:  # Only positive similarities
                user_rating_for_similar = self.user_item_matrix.loc[user_id, similar_item]
                
                numerator += similarity * user_rating_for_similar
                denominator += abs(similarity)
        
        if denominator == 0:
            prediction = self.mean_user_ratings[user_id]
        else:
            prediction = numerator / denominator
        
        # Clamp prediction to valid range
        return max(1.0, min(5.0, prediction))
    
    def get_ubcf_recommendations(self, user_id, n_recommendations=10, k_users=50):
        """
        Get recommendations using User-Based Collaborative Filtering
        """
        self.log(f"Getting UBCF recommendations for user {user_id}")
        
        if self.user_similarity_matrix is None:
            self.calculate_user_similarity()
        
        if user_id not in self.user_item_matrix.index:
            return []
        
        # Get items user hasn't rated
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        recommendations = []
        
        for item_id in unrated_items:
            predicted_rating = self.predict_rating_ubcf(user_id, item_id, k=k_users)
            
            # Get reasoning
            reason = self._get_ubcf_reason(user_id, item_id, k_users)
            
            recommendations.append({
                'product_id': item_id,
                'predicted_rating': predicted_rating,
                'method': 'UBCF',
                'reasoning': reason
            })
        
        # Sort by predicted rating
        recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return recommendations[:n_recommendations]
    
    def get_ibcf_recommendations(self, user_id, n_recommendations=10, k_items=50):
        """
        Get recommendations using Item-Based Collaborative Filtering
        """
        self.log(f"Getting IBCF recommendations for user {user_id}")
        
        if self.item_similarity_matrix is None:
            self.calculate_item_similarity()
        
        if user_id not in self.user_item_matrix.index:
            return []
        
        # Get items user hasn't rated
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        recommendations = []
        
        for item_id in unrated_items:
            predicted_rating = self.predict_rating_ibcf(user_id, item_id, k=k_items)
            
            # Get reasoning
            reason = self._get_ibcf_reason(user_id, item_id, k_items)
            
            recommendations.append({
                'product_id': item_id,
                'predicted_rating': predicted_rating,
                'method': 'IBCF',
                'reasoning': reason
            })
        
        # Sort by predicted rating
        recommendations.sort(key=lambda x: x['predicted_rating'], reverse=True)
        return recommendations[:n_recommendations]
    
    def _get_ubcf_reason(self, user_id, item_id, k=50):
        """
        Generate reasoning for UBCF recommendation
        """
        try:
            if user_id not in self.user_similarity_matrix.index:
                return "توصیه بر اساس محبوبیت عمومی"
            
            # Get similar users who rated this item
            user_similarities = self.user_similarity_matrix.loc[user_id].drop(user_id)
            rated_users = self.user_item_matrix[item_id]
            rated_users = rated_users[rated_users > 0]
            common_users = user_similarities.index.intersection(rated_users.index)
            
            if len(common_users) == 0:
                return "توصیه بر اساس میانگین محصول"
            
            similar_users = user_similarities.loc[common_users].nlargest(k)
            top_3_similarities = similar_users.head(3)
            
            avg_similarity = similar_users.mean()
            avg_rating = rated_users.loc[similar_users.index].mean()
            
            reason_parts = [
                f"بر اساس {len(similar_users)} کاربر مشابه",
                f"شباهت متوسط: {avg_similarity:.2f}",
                f"امتیاز متوسط آنها: {avg_rating:.1f}/5"
            ]
            
            return " | ".join(reason_parts)
            
        except Exception:
            return "توصیه بر اساس الگوریتم UBCF"
    
    def _get_ibcf_reason(self, user_id, item_id, k=50):
        """
        Generate reasoning for IBCF recommendation
        """
        try:
            if item_id not in self.item_similarity_matrix.index:
                return "توصیه بر اساس سلیقه شما"
            
            # Get similar items rated by this user
            item_similarities = self.item_similarity_matrix.loc[item_id].drop(item_id)
            user_ratings = self.user_item_matrix.loc[user_id]
            rated_items = user_ratings[user_ratings > 0]
            common_items = item_similarities.index.intersection(rated_items.index)
            
            if len(common_items) == 0:
                return "توصیه بر اساس سلیقه عمومی شما"
            
            similar_items = item_similarities.loc[common_items].nlargest(k)
            top_3_similarities = similar_items.head(3)
            
            avg_similarity = similar_items.mean()
            avg_your_rating = rated_items.loc[similar_items.index].mean()
            
            reason_parts = [
                f"شبیه به {len(similar_items)} محصول پسندیده شما",
                f"شباهت متوسط: {avg_similarity:.2f}",
                f"امتیاز شما به محصولات مشابه: {avg_your_rating:.1f}/5"
            ]
            
            return " | ".join(reason_parts)
            
        except Exception:
            return "توصیه بر اساس الگوریتم IBCF"
    
    def get_similarity_info(self, user_id=None, item_id=None):
        """
        Get similarity information for debugging
        """
        info = {}
        
        if self.user_similarity_matrix is not None:
            info['user_similarity_shape'] = self.user_similarity_matrix.shape
            if user_id and user_id in self.user_similarity_matrix.index:
                top_similar_users = self.user_similarity_matrix.loc[user_id].nlargest(6)[1:]  # Exclude self
                info['top_similar_users'] = top_similar_users.to_dict()
        
        if self.item_similarity_matrix is not None:
            info['item_similarity_shape'] = self.item_similarity_matrix.shape
            if item_id and item_id in self.item_similarity_matrix.index:
                top_similar_items = self.item_similarity_matrix.loc[item_id].nlargest(6)[1:]  # Exclude self
                info['top_similar_items'] = top_similar_items.to_dict()
        
        if self.user_item_matrix is not None:
            info['user_item_matrix_shape'] = self.user_item_matrix.shape
            info['non_zero_entries'] = (self.user_item_matrix > 0).sum().sum()
            info['sparsity'] = 1 - (info['non_zero_entries'] / (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]))
        
        return info
    
    def _manual_cosine_similarity(self, matrix):
        """
        Manual cosine similarity calculation when sklearn is not available
        """
        similarity_matrix = np.zeros((len(matrix), len(matrix)))
        
        for i, (idx1, row1) in enumerate(matrix.iterrows()):
            for j, (idx2, row2) in enumerate(matrix.iterrows()):
                if i <= j:  # Only calculate upper triangle
                    # Calculate cosine similarity manually
                    dot_product = np.dot(row1.values, row2.values)
                    norm1 = np.linalg.norm(row1.values)
                    norm2 = np.linalg.norm(row2.values)
                    
                    if norm1 == 0 or norm2 == 0:
                        similarity = 0
                    else:
                        similarity = dot_product / (norm1 * norm2)
                    
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity  # Symmetric matrix
        
        return pd.DataFrame(
            similarity_matrix,
            index=matrix.index,
            columns=matrix.index
        )
