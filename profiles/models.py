from django.db import models
from django.contrib.auth.models import User
from mainpage.models import Product

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/',default=None ,blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class ShoppingCartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"

    def total_price(self):
        return self.product.price * self.quantity
