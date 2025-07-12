from django.db import models
from django.contrib.auth.models import User
import uuid

class Product(models.Model):

    CATEGORY_CHOICES = [
        ('cleanser', 'پاک‌کننده'),
        ('toner', 'تونر'),
        ('serum', 'سرم'),
        ('moisturizer', 'مرطوب‌کننده'),
        ('sunscreen', 'ضدآفتاب'),
        ('eye_cream', 'کرم دور چشم'),
        ('mask', 'ماسک صورت'),
        ('exfoliator', 'لایه‌بردار'),
        ('treatment', 'درمان متمرکز'),  # مثل ضدجوش یا ضدلک
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


    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    brand_en = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    skin_types = models.JSONField()
    skin_types_en = models.JSONField()
    concerns_targeted = models.JSONField()
    ingredients = models.JSONField()
    price = models.PositiveIntegerField()
    rating = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='product_images/', default='product_images/default.png')
    views = models.PositiveIntegerField(default=0)
    tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True, verbose_name='معرفی محصول')
    usage = models.TextField(blank=True, null=True, verbose_name='نحوه مصرف')
    suitable_for = models.CharField(max_length=255, blank=True, null=True, verbose_name='مناسب برای')

    def __str__(self):
        return f"{self.name} ({self.brand})"

    @property
    def average_rating(self):
        comments = self.comments.all()
        if not comments.exists():
            return 0
        return round(sum(comment.rating for comment in comments) / comments.count(), 1)


# script for add products to database
'''
import random
from mainpage.models import Product

# نام‌های فارسی و انگلیسی محصولات (با تطابق ایندکس)
names = [
    'کرم مرطوب‌کننده', 'ضدآفتاب', 'کرم شب', 'تونر روشن‌کننده', 'ژل شستشوی صورت',
    'کرم ضدلک', 'ماسک زغالی', 'سرم ویتامین C', 'اسکراب قهوه', 'کرم دور چشم',
    'پاک‌کننده آرایش دوفاز', 'میست صورت آبرسان', 'کرم لیفتینگ', 'سرم رتینول',
    'آمپول بازسازی‌کننده', 'کرم ضدجوش', 'فوم پاک‌کننده', 'ژل آبرسان سبک',
    'اسنس مغذی', 'پچ زیر چشم طلا'
]
names_en = [
    'Moisturizing Cream', 'Sunscreen', 'Night Cream', 'Brightening Toner', 'Facial Cleansing Gel',
    'Anti-Spot Cream', 'Charcoal Mask', 'Vitamin C Serum', 'Coffee Scrub', 'Eye Cream',
    'Biphasic Makeup Remover', 'Hydrating Facial Mist', 'Lifting Cream', 'Retinol Serum',
    'Rebuilding Ampoule', 'Anti-Acne Cream', 'Foam Cleanser', 'Light Hydrating Gel',
    'Nourishing Essence', 'Gold Under-Eye Patch'
]

# برندهای فارسی و انگلیسی (با تطابق ایندکس)
brands = [
    'سینره', 'نوتروژینا', 'لورآل', 'نیوآ', 'گارنیه',
    'لاروش پوزای', 'سی‌گل', 'داو', 'فلورمار', 'ثمین',
    'اون', 'بلومه', 'استی لادر', 'ادیپیرن', 'دکتر راشل',
    'مَیبلین', 'بیودرما', 'اوردینری', 'کامان', 'الارو'
]
brands_en = [
    'Cinere', 'Neutrogena', 'L’Oreal', 'Nivea', 'Garnier',
    'La Roche-Posay', 'Seagull', 'Dove', 'Flormar', 'Samin',
    'Avene', 'Bloome', 'Estee Lauder', 'Edipierne', 'Dr. Rashel',
    'Maybelline', 'Bioderma', 'The Ordinary', 'Comeon', 'Ellaro'
]

categories = [choice[0] for choice in Product.CATEGORY_CHOICES]
skin_types_choices = [choice[1] for choice in Product.SKIN_TYPE_CHOICES]
skin_types_en_choices = [choice[0] for choice in Product.SKIN_TYPE_CHOICES]

sample_concerns = [
    'جوانسازی', 'لک صورت', 'آکنه', 'خشکی پوست', 'چربی زیاد', 'التهاب', 'خط خنده', 'قرمزی', 'کدری', 'تیرگی دور چشم'
]

sample_ingredients = [
    'هیالورونیک اسید', 'ویتامین C', 'آلوئه ورا', 'کلاژن', 'نیاسینامید',
    'سالیسلیک اسید', 'رز هیپ اویل', 'چای سبز', 'گلیکولیک اسید', 'سرامید', 'آزلائیک اسید', 'زینک'
]

sample_tags = [
    'آبرسان', 'ضدچروک', 'شاداب‌کننده', 'فاقد چربی', 'بافت سبک', 'ضد التهاب',
    'قابل استفاده زیر آرایش', 'فاقد پارابن', 'گیاهی', 'ضدحساسیت'
]

for i in range(100):
    name_index = random.randint(0, len(names) - 1)
    brand_index = random.randint(0, len(brands) - 1)
    skin_type_indecies = random.sample(range(len(skin_types_choices)), k=random.randint(1, 3))

    product = Product(
        name=names[name_index],
        name_en=names_en[name_index],
        brand=brands[brand_index],
        brand_en=brands_en[brand_index],
        category=random.choice(categories),
        skin_types=[skin_types_choices[index] for index in indecies],
        skin_types_en=[skin_types_choices_en[index] for index in indecies],
        concerns_targeted=random.sample(sample_concerns, k=random.randint(1, 3)),
        ingredients=random.sample(sample_ingredients, k=random.randint(2, 5)),
        price=random.randint(100000, 5000000),
        rating=round(random.uniform(2.0, 5.0), 1),
        image='product_images/default.jpg',
        views=random.randint(0, 1000),
        tags=random.sample(sample_tags, k=random.randint(2, 4)),
        description='لورم ایپسوم، متن ساختگی برای معرفی محصول با ویژگی‌های خاص برای انواع پوست‌ها.',
        usage='روزی دوبار روی پوست تمیز استفاده شود.',
        suitable_for='مناسب برای پوست‌های مختلف از جمله حساس و دهیدراته.',
    )
    product.save()

print("✅ 100 محصول متنوع با نام و برند منطبق ساخته شد.")

'''


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()  # 1 تا 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"نظر {self.user.username} برای {self.product.name}"
