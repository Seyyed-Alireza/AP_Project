# from django.shortcuts import render

# def mainpage(request):
#     return render(request, 'mainpage/mainpage.html')



# for test
from django.shortcuts import render

import random

names = ['کرم مرطوب‌کننده', 'ضدآفتاب', 'کرم شب', 'تونر', 'ژل شستشو', 'کرم ضدلک', 'ماسک صورت', 'سرم ویتامین C', 'اسکراب', 'کرم دور چشم']
brands = ['سینره', 'نوتروژینا', 'لورآل', 'نیوآ', 'گارنیه', 'لاروش پوزای', 'سی‌گل', 'داو', 'فلورمار', 'ثمین']


products = []

for i in range(1, 21):
    product = {
        'name': random.choice(names),
        'brand': random.choice(brands),
        'price': f'{random.randint(80000, 300000):,} تومان',
        'image': f'images/product_image.jpg',
        'views': random.randint(10, 500),
        'rating': round(random.uniform(1, 5), 1)
    }
    products.append(product)

def mainpage(request):
    return render(request, 'mainpage/mainpage.html', {'products': products})

