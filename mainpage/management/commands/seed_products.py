import random
from django.core.management.base import BaseCommand
from mainpage.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with 100 sample skincare products'

    def handle(self, *args, **kwargs):
        import random
        from mainpage.models import Product

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
                skin_types=[skin_types_choices[index] for index in skin_type_indecies],
                skin_types_en=[skin_types_en_choices[index] for index in skin_type_indecies],
                concerns_targeted=random.sample(sample_concerns, k=random.randint(1, 3)),
                ingredients=random.sample(sample_ingredients, k=random.randint(2, 5)),
                price=random.randint(100000, 5000000),
                rating=round(random.uniform(2.0, 5.0), 1),
                image='product_images/default.jpg',
                views=random.randint(10, 1000000),
                tags=random.sample(sample_tags, k=random.randint(2, 4)),
                description='لورم ایپسوم، متن ساختگی برای معرفی محصول با ویژگی‌های خاص برای انواع پوست‌ها.',
                usage='روزی دوبار روی پوست تمیز استفاده شود.',
                suitable_for='مناسب برای پوست‌های مختلف از جمله حساس و دهیدراته.',
            )
            product.save()



        self.stdout.write(self.style.SUCCESS('✅ completed'))
