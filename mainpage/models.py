from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', default='product_images/default.png')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.brand})"

    @property
    def average_rating(self):
        comments = self.comments.all()
        if not comments.exists():
            return 0
        return round(sum(comment.rating for comment in comments) / comments.count(), 1)


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()  # 1 تا 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"نظر {self.user.username} برای {self.product.name}"
