# from django.shortcuts import render

# def mainpage(request):
#     return render(request, 'mainpage/mainpage.html')



# for test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment



# create random products
# import random

# names = ['کرم مرطوب‌کننده', 'ضدآفتاب', 'کرم شب', 'تونر', 'ژل شستشو', 'کرم ضدلک', 'ماسک صورت', 'سرم ویتامین C', 'اسکراب', 'کرم دور چشم']
# brands = ['سینره', 'نوتروژینا', 'لورآل', 'نیوآ', 'گارنیه', 'لاروش پوزای', 'سی‌گل', 'داو', 'فلورمار', 'ثمین']


# products = []

# for i in range(1, 21):
#     product = {
#         'name': random.choice(names),
#         'brand': random.choice(brands),
#         'price': f'{random.randint(80000, 300000):,} تومان',
#         'image': f'images/product_image.jpg',
#         'views': random.randint(10, 500),
#         'rating': round(random.uniform(1, 5), 1)
#     }
#     products.append(product)

def mainpage(request):
    products = Product.objects.all()

    # for test ##################
    # print(">>> محصولات موجود در دیتابیس:")
    # for p in products:
    #     print(f"ID={p.id} | Name={p.name} | Brand={p.brand} | Price={p.price}")
    ##################################

    return render(request, 'mainpage/mainpage.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = product.comments.all().order_by('-created_at')

    before_commented = False
    if request.user.is_authenticated:
        before_commented = product.comments.filter(user=request.user).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')  # به صفحه لاگین بفرست

        text = request.POST.get('text')
        rating = request.POST.get('rating')

        if text and rating and rating.isdigit() and 1 <= int(rating) <= 5:
            Comment.objects.create(
                product=product,
                user=request.user,
                text=text,
                rating=int(rating)
            )
            return redirect('product_detail', pk=pk)

    return render(request, 'mainpage/product_detail.html', {
        'product': product,
        'comments': comments,
        'commented_before': before_commented
    })

