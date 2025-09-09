from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recommendations.engine import RecommendationEngine
from mainpage.models import Product


class Command(BaseCommand):
    help = 'Test the recommendation system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to test recommendations for',
        )
        parser.add_argument(
            '--method',
            type=str,
            default='comprehensive',
            choices=['ubcf', 'ibcf', 'skin', 'hybrid', 'comprehensive'],
            help='Recommendation method to test',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of recommendations to generate',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        method = options['method']
        count = options['count']
        
        if not user_id:
            # Test with first available user
            try:
                user = User.objects.first()
                if not user:
                    self.stdout.write(self.style.ERROR('No users found in the database'))
                    return
                user_id = user.id
                self.stdout.write(f'Testing with user: {user.username} (ID: {user_id})')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error finding user: {e}'))
                return
        else:
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f'Testing with user: {user.username} (ID: {user_id})')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))
                return

        # Initialize recommendation engine
        self.stdout.write(f'Initializing recommendation engine...')
        engine = RecommendationEngine()
        
        try:
            # Test different methods
            self.stdout.write(f'\n=== Testing {method.upper()} Recommendations ===')
            
            if method == 'ubcf':
                recommended_ids = engine.user_based_collaborative_filtering(user_id, count)
                self.stdout.write('Method: User-Based Collaborative Filtering')
            elif method == 'ibcf':
                recommended_ids = engine.item_based_collaborative_filtering(user_id, count)
                self.stdout.write('Method: Item-Based Collaborative Filtering')
            elif method == 'skin':
                recommended_ids = engine.skin_profile_based_recommendations(user_id, count)
                self.stdout.write('Method: Skin Profile-Based')
            elif method == 'hybrid':
                recommended_ids = engine.hybrid_recommendations(user_id, count)
                self.stdout.write('Method: Hybrid (UBCF + IBCF)')
            else:  # comprehensive
                recommended_ids = engine.get_comprehensive_recommendations(user_id, count)
                self.stdout.write('Method: Comprehensive (All methods combined)')
            
            if not recommended_ids:
                self.stdout.write(self.style.WARNING('No recommendations generated'))
                return
            
            # Get product details
            products = Product.objects.filter(id__in=recommended_ids)
            products_dict = {p.id: p for p in products}
            
            self.stdout.write(f'\nGenerated {len(recommended_ids)} recommendations:')
            self.stdout.write('-' * 80)
            
            for i, product_id in enumerate(recommended_ids, 1):
                if product_id in products_dict:
                    product = products_dict[product_id]
                    self.stdout.write(
                        f'{i:2d}. {product.name} ({product.brand}) - '
                        f'{product.price:,} تومان - '
                        f'Rating: {product.rating}/5 - '
                        f'Category: {product.get_category_display_fa()}'
                    )
                else:
                    self.stdout.write(f'{i:2d}. Product ID {product_id} (not found)')
            
            # Test data matrix creation
            self.stdout.write(f'\n=== Testing Data Matrices ===')
            
            # User-item matrix
            try:
                matrix = engine.create_user_item_matrix()
                self.stdout.write(f'User-item matrix shape: {matrix.shape}')
                self.stdout.write(f'Non-zero interactions: {(matrix > 0).sum().sum()}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating user-item matrix: {e}'))
            
            # Item features matrix
            try:
                features = engine.create_item_features_matrix()
                if features is not None:
                    self.stdout.write(f'Item features matrix shape: {features.shape}')
                else:
                    self.stdout.write(self.style.WARNING('Item features matrix not created (sklearn not available)'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating item features matrix: {e}'))
            
            # User similarity
            try:
                user_sim = engine.calculate_user_similarity()
                if user_sim is not None:
                    self.stdout.write(f'User similarity matrix shape: {user_sim.shape}')
                else:
                    self.stdout.write(self.style.WARNING('User similarity matrix not created'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error calculating user similarity: {e}'))
            
            # Test all methods for comparison
            if method == 'comprehensive':
                self.stdout.write(f'\n=== Comparison of All Methods ===')
                methods = {
                    'UBCF': engine.user_based_collaborative_filtering(user_id, 5),
                    'IBCF': engine.item_based_collaborative_filtering(user_id, 5),
                    'Skin': engine.skin_profile_based_recommendations(user_id, 5),
                    'Hybrid': engine.hybrid_recommendations(user_id, 5)
                }
                
                for method_name, recs in methods.items():
                    self.stdout.write(f'\n{method_name}: {len(recs)} recommendations')
                    for i, pid in enumerate(recs[:3], 1):  # Show top 3
                        if pid in products_dict:
                            p = products_dict[pid]
                            self.stdout.write(f'  {i}. {p.name} ({p.brand})')
            
            self.stdout.write(self.style.SUCCESS('\n✓ Recommendation system test completed successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error testing recommendations: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
