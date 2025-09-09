from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mainpage.models import Product
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from quiz.models import SkinProfile
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Generate sample data for recommendation system testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of sample users to create',
        )
        parser.add_argument(
            '--interactions',
            type=int,
            default=500,
            help='Number of sample interactions to create',
        )

    def handle(self, *args, **options):
        self.stdout.write('Generating sample recommendation data...')
        
        # Get existing products
        products = list(Product.objects.all())
        if not products:
            self.stdout.write(self.style.ERROR('No products found. Please add products first.'))
            return
        
        users_count = options['users']
        interactions_count = options['interactions']
        
        # Create sample users if needed
        existing_users = User.objects.count()
        if existing_users < users_count:
            self.stdout.write(f'Creating {users_count - existing_users} sample users...')
            for i in range(existing_users, users_count):
                user = User.objects.create_user(
                    username=f'testuser_{i}',
                    email=f'testuser_{i}@example.com',
                    password='testpass123'
                )
                
                # Create skin profile for user
                SkinProfile.objects.create(
                    user=user,
                    quiz_completed=random.choice([True, False]),
                    skin_type=random.sample(['dry', 'oily', 'sensitive', 'combination', 'normal'], 
                                          random.randint(1, 3)),
                    acne=random.randint(0, 5),
                    sensitivity=random.randint(0, 5),
                    dryness=random.randint(0, 5),
                    oiliness=random.randint(0, 5),
                    redness=random.randint(0, 5),
                )
        
        users = list(User.objects.all()[:users_count])
        
        # Generate sample interactions
        self.stdout.write(f'Generating {interactions_count} sample interactions...')
        interaction_types = ['view', 'like', 'wishlist', 'cart', 'purchase']
        
        for i in range(interactions_count):
            user = random.choice(users)
            product = random.choice(products)
            interaction_type = random.choice(interaction_types)
            
            # Create interaction
            ProductSearchHistory.objects.create(
                user=user,
                product=product,
                interaction_type=interaction_type,
                timestamp=datetime.now() - timedelta(days=random.randint(0, 90))
            )
            
            # If it's a purchase, also create purchase history
            if interaction_type == 'purchase':
                ProductPurchaseHistory.objects.create(
                    user=user,
                    product=product,
                    purchase_count=random.randint(1, 3),
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 90))
                )
        
        # Generate some correlated interactions (users with similar preferences)
        self.stdout.write('Generating correlated interactions...')
        
        # Group products by category
        categories = {}
        for product in products:
            if product.category not in categories:
                categories[product.category] = []
            categories[product.category].append(product)
        
        # Create user clusters with similar preferences
        for category, category_products in categories.items():
            if len(category_products) < 3:
                continue
                
            # Select a subset of users for this category
            category_users = random.sample(users, min(len(users)//3, 15))
            
            for user in category_users:
                # Each user in cluster interacts with 3-7 products from this category
                num_interactions = random.randint(3, min(7, len(category_products)))
                selected_products = random.sample(category_products, num_interactions)
                
                for product in selected_products:
                    interaction_type = random.choices(
                        interaction_types,
                        weights=[5, 3, 2, 2, 1],  # More views, fewer purchases
                        k=1
                    )[0]
                    
                    ProductSearchHistory.objects.create(
                        user=user,
                        product=product,
                        interaction_type=interaction_type,
                        timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated sample data:\n'
                f'- {users_count} users\n'
                f'- {interactions_count} base interactions\n'
                f'- Additional correlated interactions\n'
                f'- Skin profiles for all users'
            )
        )
