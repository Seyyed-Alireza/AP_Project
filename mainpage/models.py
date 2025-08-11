from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from quiz.models import SkinProfile

class Product(models.Model):

    NAMES = [
        'کرم مرطوب‌کننده', 'ضدآفتاب', 'کرم شب', 'تونر روشن‌کننده', 'ژل شستشوی صورت',
        'کرم ضدلک', 'ماسک زغالی', 'سرم ویتامین C', 'اسکراب قهوه', 'کرم دور چشم',
        'پاک‌کننده آرایش دوفاز', 'میست صورت آبرسان', 'کرم لیفتینگ', 'سرم رتینول',
        'آمپول بازسازی‌کننده', 'کرم ضدجوش', 'فوم پاک‌کننده', 'ژل آبرسان سبک',
        'اسنس مغذی', 'پچ زیر چشم طلا'
    ]

    NAMES_EN = [
        'Moisturizing Cream', 'Sunscreen', 'Night Cream', 'Brightening Toner', 'Facial Cleansing Gel',
        'Anti-Spot Cream', 'Charcoal Mask', 'Vitamin C Serum', 'Coffee Scrub', 'Eye Cream',
        'Biphasic Makeup Remover', 'Hydrating Facial Mist', 'Lifting Cream', 'Retinol Serum',
        'Rebuilding Ampoule', 'Anti-Acne Cream', 'Foam Cleanser', 'Light Hydrating Gel',
        'Nourishing Essence', 'Gold Under-Eye Patch'
    ]

    BRANDS = [
        'سینره', 'نوتروژینا', 'لورآل', 'نیوآ', 'گارنیه',
        'لاروش پوزای', 'سی‌گل', 'داو', 'فلورمار', 'ثمین',
        'اون', 'بلومه', 'استی لادر', 'ادیپیرن', 'دکتر راشل',
        'مَیبلین', 'بیودرما', 'اوردینری', 'کامان', 'الارو'
    ]

    CATEGORY_CHOICES = [
        ('cleanser', 'پاک‌کننده'),
        ('toner', 'تونر'),
        ('serum', 'سرم'),
        ('moisturizer', 'مرطوب‌کننده'),
        ('sunscreen', 'ضدآفتاب'),
        ('eye_cream', 'کرم دور چشم'),
        ('mask', 'ماسک صورت'),
        ('exfoliator', 'لایه‌بردار'),
        ('treatment', 'درمان متمرکز'),
        ('oil', 'روغن صورت'),
        ('mist', 'اسپری/میست صورت'),
        ('lip_care', 'مراقبت لب'),
        ('ampoule', 'آمپول'),
        ('essence', 'اسنس'),
        ('makeup_remover', 'پاک‌کننده آرایش'),
        ('spot_patch', 'پچ ضدجوش'),
    ]

    SKIN_TYPE_CHOICES = [
        ('dry', 'خشک'),
        ('oily', 'چرب'),
        ('sensitive', 'حساس'),
        ('combination', 'مختلط'),
        ('normal', 'نرمال'),
    ]

    SAMPLE_CONCERNS = [
        'جوانسازی', 'لک صورت', 'آکنه', 'خشکی پوست', 'چربی زیاد', 'التهاب', 'خط خنده', 'قرمزی', 'کدری', 'تیرگی دور چشم'
    ]

    # SAMPLE_CONCERNS = SkinProfile.SKIN_FEATURES


    name = models.CharField(max_length=100, verbose_name="نام")
    name_en = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, verbose_name="برند")
    brand_en = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    skin_types = MultiSelectField(choices=SKIN_TYPE_CHOICES, max_length=100)
    # skin_types_en = models.JSONField()
    concerns_targeted = models.JSONField()
    ingredients = models.JSONField(verbose_name="محتویات")
    price = models.PositiveIntegerField()
    rating = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='product_images/', default='product_images/default.png')
    views = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    likes = models.PositiveIntegerField(default=0)
    tags = models.JSONField()
    sales_count = models.PositiveIntegerField(default=0, verbose_name="تعداد فروش")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True, verbose_name='معرفی محصول')
    usage = models.TextField(blank=True, null=True, verbose_name='نحوه مصرف')
    suitable_for = models.CharField(max_length=255, blank=True, null=True, verbose_name='مناسب برای')

    def get_skin_types_fa(self):
        return [dict(self.SKIN_TYPE_CHOICES).get(st, st) for st in self.skin_types]
    
    def get_category_display_fa(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

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
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"نظر {self.user.username} برای {self.product.name}"
