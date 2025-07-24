from django.db import models
from django.contrib.auth.models import User
from mainpage.models import Product

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} has serched: {self.query}"
    
class ProductSearchHistory(models.Model):
    
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('wishlist', 'Wishlist'),
        ('cart', 'Cart'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='browsing_histories')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='browsing_histories')
    timestamp = models.DateTimeField(auto_now_add=True)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)

    def __str__(self):
        return f'{self.user.username} - {self.interaction_type} - {self.product}'

