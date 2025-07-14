from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment
from django.db.models import Q
from django.http import JsonResponse


def mainpage(request):
    query = request.GET.get('q')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(name_en__icontains=query) |
            Q(brand__icontains=query) |
            Q(brand_en__icontains=query)
        )

    return render(request, 'mainpage/mainpage.html', {'products': products})

#####################################################################

from difflib import SequenceMatcher
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
def search(request):
    full_query = request.GET.get('q')
    query_words = full_query.lower().split()
    products = Product.objects.all()
    results = []
    brands = [
        'سینره', 'نوتروژینا', 'لورآل', 'نیوآ', 'گارنیه',
        'لاروش پوزای', 'سی‌گل', 'داو', 'فلورمار', 'ثمین',
        'اون', 'بلومه', 'استی لادر', 'ادیپیرن', 'دکتر راشل',
        'مَیبلین', 'بیودرما', 'اوردینری', 'کامان', 'الارو'
    ]

    brand_focus = False
    # for i, word in enumerate(query_words):
    #     if word in brands:
    #         brand_focus = True
    #         query_words.pop(i)
    #     for brand in brands:
    #         print(similarity(word, brand))
    print(query_words)
    for product in products:
        score = 0
        product_name = product.name.lower()
        product_brand = product.brand.lower()

        for word in query_words:
            if word in product_name.split():
                score += 5
            elif word in product_brand:
                score += 15
            else:
                for p_word in product_name.split():
                    score += similarity(p_word, product_name) * 2
                brand_similarity = similarity(word, product_brand)
                if brand_similarity >= 0.75:
                    score += brand_similarity * 10
                # score += similarity(word, product_brand) * (3.5 if brand_focus else 1.5)

        if score > 1:
            results.append((product, score))
    results.sort(key=lambda x: x[1], reverse=True)
    final_products = [r[0] for r in results][:500]

    print(len(final_products))
    return render(request, 'mainpage/mainpage.html', {'products': final_products})

#####################################################################

# def live_search(request):
    full_query = request.GET.get('q')
    query_words = full_query.lower().split()
    results = []

    if full_query:
        product_names = Product.objects.filter(
            Q(name__icontains=full_query) |
            Q(name_en__icontains=full_query)
        ).values_list('name', flat=True).distinct()

        brand_names = Product.objects.filter(
            Q(brand__icontains=full_query) |
            Q(brand_en__icontains=full_query)
        ).values_list('brand', flat=True).distinct()

        for name in product_names:
            if name not in seen:
                seen.add(name)
                results.append({'type': 'product', 'name': name})

        for brand in brand_names:
            label = f"برند {brand}"
            if label not in seen:
                seen.add(label)
                results.append({'type': 'brand', 'name': label})

        results = results[:15]

    return JsonResponse({'results': results})


from django.http import JsonResponse

def live_search(request):
    full_query = request.GET.get('q')
    if not full_query:
        return JsonResponse({'results': []})

    query_words = full_query.lower().split()
    products = Product.objects.all()
    results = []

    brand_focus = False
    if 'برند' in query_words:
        brand_focus = True
        query_words.remove('برند')

    for product in products:
        score = 0
        product_name = product.name.lower()
        product_brand = product.brand.lower()

        for word in query_words:
            if word in product_name.split():
                score += 5
            elif word in product_brand:
                score += 10 if brand_focus else 3
            else:
                for p_word in product_name.split():
                    score += similarity(p_word, product_name) * 2
                score += similarity(word, product_brand) * (3.5 if brand_focus else 1.5)

        if score > 3:
            results.append((product, score))

    results.sort(key=lambda x: x[1], reverse=True)
    seen_names = set()
    final_products = []
    for product, score in results:
        name = product.name.strip().lower()
        if name not in seen_names:
            seen_names.add(name)
            final_products.append(product)
        if len(final_products) >= 15:
            break


    suggestions = []
    for product in final_products:
        suggestions.append({
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'price': product.price,
            'image_url': product.image.url if product.image else '',
            'url': product.get_absolute_url() if hasattr(product, 'get_absolute_url') else ''
        })

    return JsonResponse({'results': suggestions})

#######################################################################

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.views += 1
    product.save(update_fields=['views'])

    comments = product.comments.all().order_by('-created_at')

    before_commented = False
    if request.user.is_authenticated:
        before_commented = product.comments.filter(user=request.user).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

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

