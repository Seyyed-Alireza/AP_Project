import pandas as pd
import numpy as np
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Avg, Q, F
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from mainpage.models import Product, Comment
from quiz.models import SkinProfile
import json
import math
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from django.utils import timezone

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class AdvancedRecommendationEngine:
    """
    Advanced Recommendation Engine with sophisticated algorithms and detailed reasoning
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.item_features_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_profiles = None
        self.item_profiles = None
        self.interaction_weights = {
            'view': 1.0,
            'like': 3.0,
            'wishlist': 4.0,
            'cart': 5.0,
            'purchase': 10.0
        }
        self.time_decay_factor = 0.95  # Decay factor for older interactions
        self.debug = False
    
    def log(self, message):
        """Debug logging"""
        if self.debug:
            print(f"[RecommendationEngine] {message}")
    
    def create_enhanced_user_item_matrix(self):
        """
        Creates enhanced user-item interaction matrix with time decay and weighted interactions
        """
        self.log("Creating enhanced user-item matrix...")
        
        users = User.objects.all()
        products = Product.objects.all()
        
        user_ids = [u.id for u in users]
        product_ids = [p.id for p in products]
        
        matrix = pd.DataFrame(0.0, index=user_ids, columns=product_ids)
        
        # Current time for decay calculation
        now = timezone.now()
        
        # Add purchase history with high weight and quantity
        purchases = ProductPurchaseHistory.objects.all()
        for purchase in purchases:
            days_ago = (now - purchase.timestamp).days
            time_weight = self.time_decay_factor ** (days_ago / 30)  # Monthly decay
            score = purchase.purchase_count * self.interaction_weights['purchase'] * time_weight
            matrix.loc[purchase.user.id, purchase.product.id] += score
        
        # Add interaction history with time decay
        interactions = ProductSearchHistory.objects.all()
        for interaction in interactions:
            days_ago = (now - interaction.timestamp).days
            time_weight = self.time_decay_factor ** (days_ago / 30)
            weight = self.interaction_weights.get(interaction.interaction_type, 1.0)
            score = weight * time_weight
            matrix.loc[interaction.user.id, interaction.product.id] += score
        
        # Add ratings with emphasis on higher ratings
        comments = Comment.objects.all()
        for comment in comments:
            days_ago = (now - comment.created_at).days if hasattr(comment, 'created_at') else 0
            time_weight = self.time_decay_factor ** (days_ago / 30)
            # Emphasize higher ratings more
            rating_weight = (comment.rating / 5.0) ** 2
            score = rating_weight * 3.0 * time_weight
            matrix.loc[comment.user.id, comment.product.id] += score
        
        self.user_item_matrix = matrix
        return matrix
    
    def create_advanced_item_features_matrix(self):
        """
        Creates advanced item features matrix with semantic understanding
        """
        self.log("Creating advanced item features matrix...")
        
        if not SKLEARN_AVAILABLE:
            return None
        
        products = Product.objects.all()
        product_ids = []
        feature_vectors = []
        
        for product in products:
            # Enhanced feature extraction
            features = {
                'category': product.category,
                'brand': product.brand,
                'skin_types': ' '.join(product.skin_types) if product.skin_types else '',
                'concerns': ' '.join(product.concerns_targeted) if product.concerns_targeted else '',
                'ingredients': ' '.join(product.ingredients) if product.ingredients else '',
                'tags': ' '.join(product.tags) if product.tags else '',
                'price_tier': self._get_advanced_price_tier(product.price),
                'rating_tier': self._get_advanced_rating_tier(product.rating),
                'popularity_tier': self._get_popularity_tier(product.sales_count, product.views),
                'age_category': self._get_product_age_category(product.created_at)
            }
            
            # Create semantic text representation
            semantic_text = f"""
            {features['category']} {features['brand']} 
            {features['skin_types']} {features['concerns']} 
            {features['ingredients']} {features['tags']}
            {features['price_tier']} {features['rating_tier']} 
            {features['popularity_tier']} {features['age_category']}
            """.strip()
            
            feature_vectors.append(semantic_text)
            product_ids.append(product.id)
        
        # Create advanced TF-IDF with n-grams for better semantic understanding
        vectorizer = TfidfVectorizer(
            max_features=2000, 
            ngram_range=(1, 2),  # Include bigrams
            min_df=1,
            max_df=0.95,
            stop_words=None
        )
        
        tfidf_matrix = vectorizer.fit_transform(feature_vectors)
        
        self.item_features_matrix = pd.DataFrame(
            tfidf_matrix.toarray(),
            index=product_ids,
            columns=vectorizer.get_feature_names_out()
        )
        
        return self.item_features_matrix
    
    def _get_advanced_price_tier(self, price):
        """Enhanced price categorization"""
        if price < 50000:
            return 'بسیار_ارزان'
        elif price < 100000:
            return 'ارزان'
        elif price < 200000:
            return 'متوسط_پایین'
        elif price < 400000:
            return 'متوسط'
        elif price < 700000:
            return 'متوسط_بالا'
        elif price < 1000000:
            return 'گران'
        else:
            return 'لوکس'
    
    def _get_advanced_rating_tier(self, rating):
        """Enhanced rating categorization"""
        if rating < 1.5:
            return 'ضعیف_خیلی'
        elif rating < 2.5:
            return 'ضعیف'
        elif rating < 3.5:
            return 'متوسط'
        elif rating < 4.0:
            return 'خوب'
        elif rating < 4.5:
            return 'خیلی_خوب'
        else:
            return 'عالی'
    
    def _get_popularity_tier(self, sales_count, views):
        """Determine popularity tier based on sales and views"""
        popularity_score = sales_count * 5 + views * 0.1
        
        if popularity_score < 10:
            return 'جدید'
        elif popularity_score < 50:
            return 'کم_محبوب'
        elif popularity_score < 200:
            return 'متوسط_محبوب'
        elif popularity_score < 500:
            return 'محبوب'
        else:
            return 'خیلی_محبوب'
    
    def _get_product_age_category(self, created_at):
        """Categorize product by age"""
        if not created_at:
            return 'قدیمی'
        
        days_old = (timezone.now() - created_at).days
        
        if days_old < 7:
            return 'جدید'
        elif days_old < 30:
            return 'اخیر'
        elif days_old < 90:
            return 'نسبتا_جدید'
        elif days_old < 365:
            return 'متوسط'
        else:
            return 'قدیمی'
    
    def calculate_advanced_user_similarity(self):
        """
        Calculate user similarity with multiple factors
        """
        self.log("Calculating advanced user similarity...")
        
        if self.user_item_matrix is None:
            self.create_enhanced_user_item_matrix()
        
        if not SKLEARN_AVAILABLE:
            return None
        
        # Normalize the matrix
        scaler = StandardScaler()
        normalized_matrix = scaler.fit_transform(self.user_item_matrix.fillna(0))
        
        # Calculate cosine similarity
        user_similarity = cosine_similarity(normalized_matrix)
        
        self.user_similarity_matrix = pd.DataFrame(
            user_similarity,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        return self.user_similarity_matrix
    
    def calculate_advanced_item_similarity(self):
        """
        Calculate item similarity using multiple methods
        """
        self.log("Calculating advanced item similarity...")
        
        if self.item_features_matrix is None:
            self.create_advanced_item_features_matrix()
        
        if self.item_features_matrix is None:
            return None
        
        # Calculate content-based similarity
        content_similarity = cosine_similarity(self.item_features_matrix)
        
        # Calculate collaborative similarity if we have interaction data
        collab_similarity = None
        if self.user_item_matrix is not None:
            # Transpose to get item-user matrix
            item_user_matrix = self.user_item_matrix.T.fillna(0)
            if len(item_user_matrix) > 0:
                collab_similarity = cosine_similarity(item_user_matrix)
        
        # Combine content and collaborative similarities
        if collab_similarity is not None:
            combined_similarity = 0.7 * content_similarity + 0.3 * collab_similarity
        else:
            combined_similarity = content_similarity
        
        self.item_similarity_matrix = pd.DataFrame(
            combined_similarity,
            index=self.item_features_matrix.index,
            columns=self.item_features_matrix.index
        )
        
        return self.item_similarity_matrix
    def advanced_user_based_collaborative_filtering(self, user_id, n_recommendations=10):
        """
        Advanced UBCF with detailed reasoning and confidence scores
        """
        self.log(f"Running advanced UBCF for user {user_id}")
        
        if self.user_similarity_matrix is None:
            self.calculate_advanced_user_similarity()
        
        if user_id not in self.user_similarity_matrix.index:
            return self._get_advanced_popular_products(n_recommendations)
        
        # Get top similar users with minimum similarity threshold
        similar_users = self.user_similarity_matrix[user_id].sort_values(ascending=False)[1:21]
        similar_users = similar_users[similar_users > 0.1]  # Minimum similarity threshold
        
        if len(similar_users) == 0:
            return self._get_advanced_popular_products(n_recommendations)
        
        user_products = self.user_item_matrix.loc[user_id]
        unrated_products = user_products[user_products == 0].index
        
        recommendations = []
        
        for product_id in unrated_products:
            scores = []
            similar_user_details = []
            
            for similar_user_id, similarity in similar_users.items():
                user_rating = self.user_item_matrix.loc[similar_user_id, product_id]
                if user_rating > 0:
                    scores.append(similarity * user_rating)
                    similar_user_details.append({
                        'user_id': similar_user_id,
                        'similarity': similarity,
                        'rating': user_rating
                    })
            
            if len(scores) >= 2:  # Need at least 2 similar users
                prediction_score = sum(scores) / len(scores)
                confidence = min(len(scores) / 5.0, 1.0)  # Confidence based on number of similar users
                
                # Get product details for reasoning
                try:
                    product = Product.objects.get(id=product_id)
                    
                    # Create detailed reasoning
                    top_similar_users = sorted(similar_user_details, key=lambda x: x['similarity'], reverse=True)[:3]
                    
                    reasoning_parts = [
                        f"بر اساس {len(similar_user_details)} کاربر مشابه با شما",
                        f"اعتماد: {confidence*100:.0f}%",
                        f"امتیاز پیش‌بینی: {prediction_score:.1f}/10"
                    ]
                    
                    # Add specific similar user info
                    if top_similar_users:
                        similarities = [f"{u['similarity']:.2f}" for u in top_similar_users]
                        reasoning_parts.append(f"شباهت با برترین کاربران: {', '.join(similarities)}")
                    
                    # Add product category and brand info
                    reasoning_parts.append(f"دسته: {product.get_category_display_fa()}")
                    reasoning_parts.append(f"برند: {product.brand}")
                    
                    reasoning = " | ".join(reasoning_parts)
                    
                    recommendations.append({
                        'product_id': product_id,
                        'score': prediction_score * confidence,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'method': 'UBCF_Advanced'
                    })
                    
                except Product.DoesNotExist:
                    continue
        
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:n_recommendations]
    
    def advanced_item_based_collaborative_filtering(self, user_id, n_recommendations=10):
        """
        Advanced IBCF with detailed reasoning
        """
        self.log(f"Running advanced IBCF for user {user_id}")
        
        if self.item_similarity_matrix is None:
            self.calculate_advanced_item_similarity()
        
        if self.user_item_matrix is None:
            self.create_enhanced_user_item_matrix()
        
        if user_id not in self.user_item_matrix.index:
            return self._get_advanced_popular_products(n_recommendations)
        
        user_products = self.user_item_matrix.loc[user_id]
        liked_products = user_products[user_products > 2.0]  # Products user actually liked
        
        if len(liked_products) == 0:
            return self._get_advanced_popular_products(n_recommendations)
        
        recommendations = []
        unrated_products = user_products[user_products == 0].index
        
        for product_id in unrated_products:
            if product_id not in self.item_similarity_matrix.index:
                continue
            
            similarities_scores = []
            similar_product_details = []
            
            for liked_product_id, user_rating in liked_products.items():
                if liked_product_id in self.item_similarity_matrix.columns:
                    similarity = self.item_similarity_matrix.loc[product_id, liked_product_id]
                    if similarity > 0.15:  # Minimum similarity threshold
                        similarities_scores.append(similarity * user_rating)
                        similar_product_details.append({
                            'product_id': liked_product_id,
                            'similarity': similarity,
                            'user_rating': user_rating
                        })
            
            if len(similarities_scores) >= 1:
                prediction_score = sum(similarities_scores) / len(similarities_scores)
                confidence = min(len(similarities_scores) / 3.0, 1.0)
                
                try:
                    product = Product.objects.get(id=product_id)
                    
                    # Create detailed reasoning
                    top_similar_products = sorted(similar_product_details, 
                                                key=lambda x: x['similarity'], reverse=True)[:3]
                    
                    reasoning_parts = [
                        f"مشابه به {len(similar_product_details)} محصول که پسندیده‌اید",
                        f"اعتماد: {confidence*100:.0f}%"
                    ]
                    
                    # Add similar product names
                    if top_similar_products:
                        try:
                            similar_names = []
                            for sim_prod in top_similar_products[:2]:
                                sim_product = Product.objects.get(id=sim_prod['product_id'])
                                similar_names.append(f"{sim_product.name[:20]}")
                            reasoning_parts.append(f"مشابه به: {', '.join(similar_names)}")
                        except:
                            pass
                    
                    # Add matching features
                    feature_matches = self._get_feature_matches(product, liked_products.index.tolist())
                    if feature_matches:
                        reasoning_parts.append(f"ویژگی‌های مشترک: {', '.join(feature_matches[:3])}")
                    
                    reasoning = " | ".join(reasoning_parts)
                    
                    recommendations.append({
                        'product_id': product_id,
                        'score': prediction_score * confidence,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'method': 'IBCF_Advanced'
                    })
                    
                except Product.DoesNotExist:
                    continue
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:n_recommendations]
    
    def advanced_skin_profile_recommendations(self, user_id, n_recommendations=10):
        """
        Advanced skin profile-based recommendations with detailed analysis
        """
        self.log(f"Running advanced skin profile recommendations for user {user_id}")
        
        try:
            user = User.objects.get(id=user_id)
            skin_profile = SkinProfile.objects.get(user=user)
        except (User.DoesNotExist, SkinProfile.DoesNotExist):
            return self._get_advanced_popular_products(n_recommendations)
        
        user_skin_types = skin_profile.skin_type
        
        # Calculate skin concern priorities with weights
        concern_weights = {
            'آکنه': skin_profile.acne,
            'حساسیت': skin_profile.sensitivity, 
            'خشکی': skin_profile.dryness,
            'چربی': skin_profile.oiliness,
            'قرمزی': skin_profile.redness,
        }
        
        # Get top concerns (score > 3)
        top_concerns = [(concern, score) for concern, score in concern_weights.items() if score > 3]
        top_concerns.sort(key=lambda x: x[1], reverse=True)
        
        products = Product.objects.all()
        recommendations = []
        
        for product in products:
            match_score = 0
            match_reasons = []
            
            # Score based on skin type match
            skin_type_matches = [st for st in user_skin_types if st in product.skin_types]
            if skin_type_matches:
                match_score += len(skin_type_matches) * 3.0
                match_reasons.append(f"مناسب برای پوست {', '.join(skin_type_matches)}")
            
            # Score based on concern matches
            concern_matches = []
            for concern, severity in top_concerns:
                if concern in product.concerns_targeted:
                    concern_score = severity / 5.0 * 4.0  # Convert to score out of 4
                    match_score += concern_score
                    concern_matches.append(concern)
            
            if concern_matches:
                match_reasons.append(f"حل مشکلات: {', '.join(concern_matches)}")
            
            # Add product quality scores
            quality_score = product.rating * 0.8 + math.log(product.sales_count + 1) * 0.3
            match_score += quality_score
            
            # Calculate confidence based on number of matches
            confidence = min((len(skin_type_matches) + len(concern_matches)) / 4.0, 1.0)
            
            if match_score > 3.0:  # Minimum threshold
                # Create detailed reasoning
                reasoning_parts = []
                reasoning_parts.extend(match_reasons)
                
                if product.rating > 4.0:
                    reasoning_parts.append(f"امتیاز بالا: {product.rating:.1f}")
                
                if product.sales_count > 100:
                    reasoning_parts.append(f"محبوب: {product.sales_count} فروش")
                
                # Add ingredient benefits
                beneficial_ingredients = self._get_beneficial_ingredients(product, top_concerns)
                if beneficial_ingredients:
                    reasoning_parts.append(f"ترکیبات مفید: {', '.join(beneficial_ingredients[:2])}")
                
                reasoning = " | ".join(reasoning_parts)
                
                recommendations.append({
                    'product_id': product.id,
                    'score': match_score * confidence,
                    'confidence': confidence,
                    'reasoning': reasoning,
                    'method': 'Skin_Profile_Advanced'
                })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:n_recommendations]
    
    def _get_feature_matches(self, product, liked_product_ids):
        """Get matching features between product and user's liked products"""
        matches = []
        
        try:
            liked_products = Product.objects.filter(id__in=liked_product_ids)
            
            # Check brand matches
            liked_brands = set(p.brand for p in liked_products)
            if product.brand in liked_brands:
                matches.append(f"برند محبوب ({product.brand})")
            
            # Check category matches
            liked_categories = set(p.category for p in liked_products)
            if product.category in liked_categories:
                matches.append(f"دسته مورد علاقه ({product.get_category_display_fa()})")
            
            # Check price range matches
            liked_price_ranges = set(self._get_advanced_price_tier(p.price) for p in liked_products)
            if self._get_advanced_price_tier(product.price) in liked_price_ranges:
                matches.append(f"محدوده قیمتی مناسب")
            
        except Exception:
            pass
        
        return matches
    
    def _get_beneficial_ingredients(self, product, top_concerns):
        """Get beneficial ingredients for user's skin concerns"""
        beneficial = []
        
        # Define beneficial ingredients for each concern
        concern_ingredients = {
            'آکنه': ['سالیسیلیک اسید', 'نیاسینامید', 'زینک', 'چای سبز'],
            'حساسیت': ['آلوئه ورا', 'کاموماyl', 'سنتلا آسیاتیکا', 'آلانتوئین'],
            'خشکی': ['هیالورونیک اسید', 'گلیسرین', 'سرامید', 'شی بوتر'],
            'چربی': ['نیاسینامید', 'سالیسیلیک اسید', 'رتینول', 'کلی'],
            'قرمزی': ['آزولن', 'آلوئه ورا', 'ویتامین E', 'کاموماyl']
        }
        
        product_ingredients = product.ingredients if product.ingredients else []
        
        for concern, _ in top_concerns:
            if concern in concern_ingredients:
                for ingredient in concern_ingredients[concern]:
                    if any(ingredient.lower() in ing.lower() for ing in product_ingredients):
                        beneficial.append(ingredient)
        
        return beneficial
    
    def _get_advanced_popular_products(self, n_recommendations=10):
        """Advanced popular products with reasoning"""
        popular_products = Product.objects.annotate(
            popularity_score=F('sales_count') * 2 + F('rating') * F('views') / 100
        ).order_by('-popularity_score')[:n_recommendations]
        
        recommendations = []
        for product in popular_products:
            reasoning_parts = [
                "محصول محبوب",
                f"امتیاز: {product.rating:.1f}",
                f"فروش: {product.sales_count}",
                f"بازدید: {product.views}"
            ]
            
            reasoning = " | ".join(reasoning_parts)
            
            recommendations.append({
                'product_id': product.id,
                'score': 5.0,  # Base score for popular items
                'confidence': 0.7,
                'reasoning': reasoning,
                'method': 'Popular_Advanced'
            })
        
        return recommendations
        """
        Creates user-item interaction matrix from purchase and interaction history
        """
        # Get all users and products
        users = User.objects.all()
        products = Product.objects.all()
        
        # Create empty matrix
        user_ids = [u.id for u in users]
        product_ids = [p.id for p in products]
        
        matrix = pd.DataFrame(0, index=user_ids, columns=product_ids)
        
        # Fill with purchase data (highest weight)
        purchases = ProductPurchaseHistory.objects.all()
        for purchase in purchases:
            matrix.loc[purchase.user.id, purchase.product.id] += purchase.purchase_count * 5
        
        # Fill with interaction data
        interactions = ProductSearchHistory.objects.all()
        interaction_weights = {
            'view': 1,
            'like': 2,
            'wishlist': 3,
            'cart': 4,
            'purchase': 5
        }
        
        for interaction in interactions:
            weight = interaction_weights.get(interaction.interaction_type, 1)
            matrix.loc[interaction.user.id, interaction.product.id] += weight
        
        # Fill with ratings
        comments = Comment.objects.all()
        for comment in comments:
            matrix.loc[comment.user.id, comment.product.id] += comment.rating
        
        self.user_item_matrix = matrix
        return matrix
    
    def create_item_features_matrix(self):
        """
        Creates item features matrix for content-based filtering
        """
        products = Product.objects.all()
        
        # Prepare feature vectors
        features_data = []
        product_ids = []
        
        for product in products:
            features = {
                'category': product.category,
                'brand': product.brand,
                'skin_types': ','.join(product.skin_types) if product.skin_types else '',
                'concerns': ','.join(product.concerns_targeted) if product.concerns_targeted else '',
                'ingredients': ','.join(product.ingredients) if product.ingredients else '',
                'tags': ','.join(product.tags) if product.tags else '',
                'price_range': self._get_price_range(product.price),
                'rating_range': self._get_rating_range(product.rating)
            }
            
            # Combine all text features
            text_features = f"{features['category']} {features['brand']} {features['skin_types']} {features['concerns']} {features['ingredients']} {features['tags']} {features['price_range']} {features['rating_range']}"
            features_data.append(text_features)
            product_ids.append(product.id)
        
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        tfidf_matrix = vectorizer.fit_transform(features_data)
        
        self.item_features_matrix = pd.DataFrame(
            tfidf_matrix.toarray(), 
            index=product_ids, 
            columns=vectorizer.get_feature_names_out()
        )
        
        return self.item_features_matrix
    
    def _get_price_range(self, price):
        """Categorize price into ranges"""
        if price < 100000:
            return 'ارزان'
        elif price < 300000:
            return 'متوسط'
        else:
            return 'گران'
    
    def _get_rating_range(self, rating):
        """Categorize rating into ranges"""
        if rating < 2:
            return 'ضعیف'
        elif rating < 3.5:
            return 'متوسط'
        elif rating < 4.5:
            return 'خوب'
        else:
            return 'عالی'
    
    def calculate_user_similarity(self):
        """
        Calculate user-user similarity matrix using cosine similarity
        """
        if self.user_item_matrix is None:
            self.create_user_item_matrix()
        
        # Calculate cosine similarity between users
        user_similarity = cosine_similarity(self.user_item_matrix)
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
        if self.item_features_matrix is None:
            self.create_item_features_matrix()
        
        # Calculate cosine similarity between items
        item_similarity = cosine_similarity(self.item_features_matrix)
        self.item_similarity_matrix = pd.DataFrame(
            item_similarity,
            index=self.item_features_matrix.index,
            columns=self.item_features_matrix.index
        )
        
        return self.item_similarity_matrix
    
    def user_based_collaborative_filtering(self, user_id, n_recommendations=10, include_reasons=False):
        """
        UBCF: Recommend products based on similar users' preferences
        """
        if self.user_similarity_matrix is None:
            self.calculate_user_similarity()
        
        if user_id not in self.user_similarity_matrix.index:
            if include_reasons:
                return self._get_popular_products_with_reasons(n_recommendations, "محصولات محبوب - کاربر جدید")
            return self._get_popular_products(n_recommendations)
        
        # Get similar users (excluding the user themselves)
        similar_users = self.user_similarity_matrix[user_id].sort_values(ascending=False)[1:11]
        
        # Get products that similar users liked but current user hasn't interacted with
        user_products = self.user_item_matrix.loc[user_id]
        unrated_products = user_products[user_products == 0].index
        
        recommendations = {}
        recommendation_reasons = {}
        
        for product_id in unrated_products:
            score = 0
            similarity_sum = 0
            contributing_users = []
            
            for similar_user_id, similarity in similar_users.items():
                if self.user_item_matrix.loc[similar_user_id, product_id] > 0:
                    score += similarity * self.user_item_matrix.loc[similar_user_id, product_id]
                    similarity_sum += abs(similarity)
                    contributing_users.append((similar_user_id, similarity))
            
            if similarity_sum > 0:
                recommendations[product_id] = score / similarity_sum
                
                # Create reason
                top_users = sorted(contributing_users, key=lambda x: x[1], reverse=True)[:3]
                user_count = len(contributing_users)
                reason = f"کاربران مشابه شما ({user_count} نفر) این محصول را پسندیده‌اند"
                recommendation_reasons[product_id] = reason
        
        # Sort and return top N recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        if include_reasons:
            return [(product_id, recommendation_reasons.get(product_id, "")) 
                   for product_id, score in sorted_recommendations[:n_recommendations]]
        else:
            return [product_id for product_id, score in sorted_recommendations[:n_recommendations]]
    
    def item_based_collaborative_filtering(self, user_id, n_recommendations=10, include_reasons=False):
        """
        IBCF: Recommend products based on item similarity
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
        recommendation_reasons = {}
        
        # For each unrated product, calculate similarity to user's rated products
        unrated_products = user_products[user_products == 0].index
        
        for product_id in unrated_products:
            if product_id not in self.item_similarity_matrix.index:
                continue
                
            score = 0
            similarity_sum = 0
            similar_products = []
            
            for rated_product_id, rating in rated_products.items():
                if rated_product_id in self.item_similarity_matrix.columns:
                    similarity = self.item_similarity_matrix.loc[product_id, rated_product_id]
                    if similarity > 0.1:  # Only consider meaningful similarities
                        score += similarity * rating
                        similarity_sum += abs(similarity)
                        similar_products.append((rated_product_id, similarity))
            
            if similarity_sum > 0:
                recommendations[product_id] = score / similarity_sum
                
                # Create reason
                similar_products.sort(key=lambda x: x[1], reverse=True)
                top_similar = similar_products[:2]
                if top_similar:
                    try:
                        from mainpage.models import Product
                        similar_names = []
                        for pid, sim in top_similar:
                            try:
                                product = Product.objects.get(id=pid)
                                similar_names.append(product.name)
                            except:
                                pass
                        if similar_names:
                            reason = f"شبیه به محصولات مورد علاقه شما: {', '.join(similar_names[:2])}"
                        else:
                            reason = "بر اساس محصولات مشابه به سلیقه شما"
                    except:
                        reason = "بر اساس محصولات مشابه به سلیقه شما"
                else:
                    reason = "بر اساس محصولات مشابه به سلیقه شما"
                
                recommendation_reasons[product_id] = reason
        
        # Sort and return top N recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        if include_reasons:
            return [(product_id, recommendation_reasons.get(product_id, "")) 
                   for product_id, score in sorted_recommendations[:n_recommendations]]
        else:
            return [product_id for product_id, score in sorted_recommendations[:n_recommendations]]
    
    def hybrid_recommendations(self, user_id, n_recommendations=10, ubcf_weight=0.5, ibcf_weight=0.5):
        """
        Hybrid approach combining UBCF and IBCF
        """
        ubcf_recs = self.user_based_collaborative_filtering(user_id, n_recommendations * 2)
        ibcf_recs = self.item_based_collaborative_filtering(user_id, n_recommendations * 2)
        
        # Combine recommendations with weights
        combined_scores = {}
        
        # Score UBCF recommendations
        for i, product_id in enumerate(ubcf_recs):
            score = (len(ubcf_recs) - i) * ubcf_weight
            combined_scores[product_id] = combined_scores.get(product_id, 0) + score
        
        # Score IBCF recommendations
        for i, product_id in enumerate(ibcf_recs):
            score = (len(ibcf_recs) - i) * ibcf_weight
            combined_scores[product_id] = combined_scores.get(product_id, 0) + score
        
        # Sort and return top N
        sorted_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return [product_id for product_id, score in sorted_recommendations[:n_recommendations]]
    
    def skin_profile_based_recommendations(self, user_id, n_recommendations=10, include_reasons=False):
        """
        Content-based recommendations based on user's skin profile
        """
        try:
            user = User.objects.get(id=user_id)
            skin_profile = SkinProfile.objects.get(user=user)
        except (User.DoesNotExist, SkinProfile.DoesNotExist):
            if include_reasons:
                return self._get_popular_products_with_reasons(n_recommendations, "محصولات محبوب - عدم تکمیل آزمون پوست")
            return self._get_popular_products(n_recommendations)
        
        # Get user's skin type and concerns
        user_skin_types = skin_profile.skin_type
        
        # Calculate skin concern scores
        concerns_scores = {
            'آکنه': skin_profile.acne,
            'حساسیت': skin_profile.sensitivity,
            'خشکی': skin_profile.dryness,
            'چربی': skin_profile.oiliness,
            'قرمزی': skin_profile.redness,
        }
        
        # Get top concerns
        top_concerns = [concern for concern, score in sorted(concerns_scores.items(), key=lambda x: x[1], reverse=True) if score > 3]
        
        # Filter products based on skin profile
        products = Product.objects.all()
        scored_products = []
        
        for product in products:
            score = 0
            reasons = []
            
            # Score based on skin type match
            skin_type_match = False
            if any(skin_type in product.skin_types for skin_type in user_skin_types):
                score += 3
                skin_type_match = True
                matching_types = [st for st in user_skin_types if st in product.skin_types]
                skin_type_names = {'dry': 'خشک', 'oily': 'چرب', 'sensitive': 'حساس', 'combination': 'مختلط', 'normal': 'نرمال'}
                type_names = [skin_type_names.get(st, st) for st in matching_types]
                reasons.append(f"مناسب برای پوست {', '.join(type_names)}")
            
            # Score based on concerns match
            concern_matches = []
            for concern in top_concerns:
                if concern in product.concerns_targeted:
                    concern_score = concerns_scores[concern] / 2
                    score += concern_score
                    concern_matches.append(concern)
            
            if concern_matches:
                reasons.append(f"مفید برای {', '.join(concern_matches)}")
            
            # Add product rating and popularity
            if product.rating > 4:
                score += product.rating * 0.5
                reasons.append(f"امتیاز بالا ({product.rating:.1f})")
            
            if product.sales_count > 50:
                score += np.log(product.sales_count + 1) * 0.3
                reasons.append("محبوب میان کاربران")
            
            # Create comprehensive reason
            if reasons:
                reason = " • ".join(reasons)
            elif skin_type_match:
                reason = "مناسب برای نوع پوست شما"
            else:
                reason = "محصول کیفی با امتیاز مناسب"
            
            if score > 0:
                scored_products.append((product.id, score, reason))
        
        # Sort and return top N
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        if include_reasons:
            return [(product_id, reason) for product_id, score, reason in scored_products[:n_recommendations]]
        else:
            return [product_id for product_id, score, reason in scored_products[:n_recommendations]]
    
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
        
        return [(product.id, reason) for product in popular_products]
    
    def get_comprehensive_recommendations(self, user_id, n_recommendations=10, include_reasons=False):
        """
        Get comprehensive recommendations using multiple algorithms
        """
        # Get recommendations from different methods
        if include_reasons:
            ubcf_recs = self.user_based_collaborative_filtering(user_id, n_recommendations, include_reasons=True)
            ibcf_recs = self.item_based_collaborative_filtering(user_id, n_recommendations, include_reasons=True)
            skin_recs = self.skin_profile_based_recommendations(user_id, n_recommendations, include_reasons=True)
        else:
            ubcf_recs = self.user_based_collaborative_filtering(user_id, n_recommendations)
            ibcf_recs = self.item_based_collaborative_filtering(user_id, n_recommendations)
            skin_recs = self.skin_profile_based_recommendations(user_id, n_recommendations)
        
        # Combine all recommendations with different weights
        final_scores = {}
        final_reasons = {}
        
        # Weight different recommendation types
        weights = {
            'ubcf': 0.3,
            'ibcf': 0.3,
            'skin': 0.4,
        }
        
        if include_reasons:
            recommendation_lists = {
                'ubcf': ubcf_recs,
                'ibcf': ibcf_recs,
                'skin': skin_recs,
            }
            
            for method, recs in recommendation_lists.items():
                weight = weights[method]
                for i, (product_id, reason) in enumerate(recs):
                    score = (len(recs) - i) * weight
                    final_scores[product_id] = final_scores.get(product_id, 0) + score
                    
                    # Combine reasons
                    if product_id not in final_reasons:
                        final_reasons[product_id] = []
                    
                    method_names = {
                        'ubcf': 'کاربران مشابه',
                        'ibcf': 'محصولات مشابه',
                        'skin': 'پروفایل پوست'
                    }
                    
                    if reason and reason not in final_reasons[product_id]:
                        final_reasons[product_id].append(f"{method_names[method]}: {reason}")
            
            # Sort and return final recommendations with combined reasons
            sorted_final = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
            result = []
            for product_id, score in sorted_final[:n_recommendations]:
                combined_reason = " | ".join(final_reasons.get(product_id, ["توصیه جامع بر اساس تحلیل سلیقه شما"]))
                result.append((product_id, combined_reason))
            return result
        else:
            recommendation_lists = {
                'ubcf': ubcf_recs,
                'ibcf': ibcf_recs,
                'skin': skin_recs,
            }
            
            for method, recs in recommendation_lists.items():
                weight = weights[method]
                for i, product_id in enumerate(recs):
                    score = (len(recs) - i) * weight
                    final_scores[product_id] = final_scores.get(product_id, 0) + score
            
            # Sort and return final recommendations
            sorted_final = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
            return [product_id for product_id, score in sorted_final[:n_recommendations]]
    
    def get_comprehensive_advanced_recommendations(self, user_id, n_recommendations=10):
        """
        Get comprehensive recommendations using advanced algorithms with detailed reasoning
        """
        self.log(f"Getting comprehensive advanced recommendations for user {user_id}")
        
        all_recommendations = []
        
        # Get recommendations from each advanced method
        methods = [
            ('ubcf_advanced', self.advanced_user_based_collaborative_filtering),
            ('ibcf_advanced', self.advanced_item_based_collaborative_filtering), 
            ('skin_advanced', self.advanced_skin_profile_recommendations)
        ]
        
        for method_name, method_func in methods:
            try:
                recs = method_func(user_id, n_recommendations * 2)  # Get more for diversity
                for rec in recs:
                    rec['method'] = method_name
                    all_recommendations.append(rec)
            except Exception as e:
                self.log(f"Error in {method_name}: {str(e)}")
                continue
        
        # Calculate dynamic weights based on data availability
        weights = self._calculate_dynamic_weights(user_id)
        
        # Apply weights to scores
        for rec in all_recommendations:
            method_key = rec['method'].replace('_advanced', '')
            if method_key in weights:
                rec['weighted_score'] = rec['score'] * weights[method_key]
            else:
                rec['weighted_score'] = rec['score']
        
        # Deduplicate and combine scores for same products
        product_scores = {}
        product_recommendations = {}
        
        for rec in all_recommendations:
            product_id = rec['product_id']
            
            if product_id not in product_scores:
                product_scores[product_id] = 0
                product_recommendations[product_id] = {
                    'reasons': [],
                    'confidence': 0,
                    'methods': []
                }
            
            # Accumulate scores
            product_scores[product_id] += rec['weighted_score']
            
            # Combine reasoning and confidence
            product_recommendations[product_id]['reasons'].append(rec['reasoning'])
            product_recommendations[product_id]['confidence'] = max(
                product_recommendations[product_id]['confidence'], 
                rec['confidence']
            )
            product_recommendations[product_id]['methods'].append(rec['method'])
        
        # Sort by final scores
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Format final recommendations
        final_recommendations = []
        for product_id, final_score in sorted_products[:n_recommendations]:
            rec_data = product_recommendations[product_id]
            
            # Create comprehensive reasoning
            method_count = len(set(rec_data['methods']))
            confidence = rec_data['confidence']
            
            reasoning_intro = f"توصیه با {method_count} روش تحلیل | اعتماد: {confidence*100:.0f}%"
            detailed_reasons = " | ".join(rec_data['reasons'][:3])  # Limit to top 3 reasons
            
            comprehensive_reasoning = f"{reasoning_intro} | {detailed_reasons}"
            
            final_recommendations.append({
                'product_id': product_id,
                'score': final_score,
                'confidence': confidence,
                'reasoning': comprehensive_reasoning,
                'method': 'Comprehensive_Advanced',
                'method_count': method_count
            })
        
        return final_recommendations
    
    def _calculate_dynamic_weights(self, user_id):
        """
        Calculate dynamic weights based on available data for the user
        """
        weights = {'ubcf': 0.4, 'ibcf': 0.3, 'skin': 0.3}  # Default weights
        
        try:
            # Check interaction history
            interaction_count = ProductSearchHistory.objects.filter(user_id=user_id).count()
            purchase_count = ProductPurchaseHistory.objects.filter(user_id=user_id).count()
            
            # Check skin profile completeness
            has_skin_profile = SkinProfile.objects.filter(user_id=user_id).exists()
            
            # Adjust weights based on data availability
            if interaction_count < 5:
                # Low interaction data - reduce UBCF, increase skin profile
                weights['ubcf'] = 0.2
                weights['skin'] = 0.5
            elif interaction_count > 20:
                # Rich interaction data - increase UBCF
                weights['ubcf'] = 0.5
                weights['ibcf'] = 0.3
                weights['skin'] = 0.2
            
            if purchase_count > 10:
                # Strong purchase history - increase collaborative methods
                weights['ubcf'] = 0.45
                weights['ibcf'] = 0.35
                weights['skin'] = 0.2
            
            if not has_skin_profile:
                # No skin profile - rely more on collaborative filtering
                weights['ubcf'] = 0.6
                weights['ibcf'] = 0.4
                weights['skin'] = 0.0
            
            # Normalize weights to sum to 1
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v/total_weight for k, v in weights.items()}
            
        except Exception as e:
            self.log(f"Error calculating dynamic weights: {str(e)}")
            # Return default weights
            weights = {'ubcf': 0.4, 'ibcf': 0.3, 'skin': 0.3}
        
        return weights


# Backward compatibility - maintain existing interface
class RecommendationEngine:
    """Backward compatibility wrapper for the advanced engine"""
    
    def __init__(self):
        self.advanced_engine = AdvancedRecommendationEngine()
    
    def create_user_item_matrix(self):
        return self.advanced_engine.create_enhanced_user_item_matrix()
    
    def create_item_features_matrix(self):
        """Legacy method for creating item features matrix"""
        return self.advanced_engine.create_advanced_item_features_matrix()
    
    def calculate_item_similarity(self):
        """Legacy method for calculating item similarity"""
        return self.advanced_engine.calculate_advanced_item_similarity()
    
    @property
    def item_similarity_matrix(self):
        """Access to the item similarity matrix"""
        return self.advanced_engine.item_similarity_matrix
    
    def user_based_collaborative_filtering(self, user_id, n_recommendations=10, include_reasons=False):
        """Legacy UBCF method"""
        try:
            advanced_recs = self.advanced_engine.advanced_user_based_collaborative_filtering(
                user_id, n_recommendations
            )
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in advanced_recs]
            else:
                return [rec['product_id'] for rec in advanced_recs]
        except:
            fallback_recs = self.advanced_engine._get_advanced_popular_products(n_recommendations)
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in fallback_recs]
            else:
                return [rec['product_id'] for rec in fallback_recs]
    
    def item_based_collaborative_filtering(self, user_id, n_recommendations=10, include_reasons=False):
        """Legacy IBCF method"""
        try:
            advanced_recs = self.advanced_engine.advanced_item_based_collaborative_filtering(
                user_id, n_recommendations
            )
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in advanced_recs]
            else:
                return [rec['product_id'] for rec in advanced_recs]
        except:
            fallback_recs = self.advanced_engine._get_advanced_popular_products(n_recommendations)
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in fallback_recs]
            else:
                return [rec['product_id'] for rec in fallback_recs]
    
    def content_based_filtering(self, user_id, n_recommendations=10, include_reasons=False):
        """Legacy content-based method"""
        try:
            advanced_recs = self.advanced_engine.advanced_skin_profile_recommendations(
                user_id, n_recommendations
            )
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in advanced_recs]
            else:
                return [rec['product_id'] for rec in advanced_recs]
        except:
            fallback_recs = self.advanced_engine._get_advanced_popular_products(n_recommendations)
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in fallback_recs]
            else:
                return [rec['product_id'] for rec in fallback_recs]
    
    def skin_profile_based_recommendations(self, user_id, n_recommendations=10, include_reasons=False):
        """Legacy skin profile method"""
        return self.content_based_filtering(user_id, n_recommendations, include_reasons)
    
    def get_comprehensive_recommendations(self, user_id, n_recommendations=10, include_reasons=False):
        """Legacy comprehensive method"""
        try:
            advanced_recs = self.advanced_engine.get_comprehensive_advanced_recommendations(
                user_id, n_recommendations
            )
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in advanced_recs]
            else:
                return [rec['product_id'] for rec in advanced_recs]
        except:
            fallback_recs = self.advanced_engine._get_advanced_popular_products(n_recommendations)
            if include_reasons:
                return [(rec['product_id'], rec['reasoning']) for rec in fallback_recs]
            else:
                return [rec['product_id'] for rec in fallback_recs]
    
    def hybrid_recommendations(self, user_id, n_recommendations=10, with_reasons=False):
        """Enhanced hybrid method with reasoning support"""
        if with_reasons:
            return self.advanced_engine.get_comprehensive_advanced_recommendations(
                user_id, n_recommendations
            )
        else:
            # Legacy format - just product IDs
            advanced_recs = self.advanced_engine.get_comprehensive_advanced_recommendations(
                user_id, n_recommendations
            )
            return [rec['product_id'] for rec in advanced_recs]
