from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment
from django.db.models import Q
from django.http import JsonResponse


<<<<<<< HEAD
def bayesian_average(product, total_rating_average):
    m = 50
    return (product.sales_count / (product.sales_count + m)) * product.rating + (m / (product.sales_count + m)) * total_rating_average

def mainpage(request):
=======
from django.db.models import Q

def mainpage(request):
    # Start with all products
>>>>>>> cff05388b6d0d45544734473f1a1b5e8cf4766f6
    products = Product.objects.all()
    results = []
    total_rating_average = sum([product.rating for product in products]) / len(products)
    max_view = max([product.views for product in products])
    for product in products:
        results.append((product, bayesian_average(product, total_rating_average) + (product.views / max_view) / 2))

<<<<<<< HEAD
    results.sort(key=lambda x: x[1], reverse=True)
    final_products = [p[0] for p in results]
    
    return render(request, 'mainpage/mainpage.html', {'products': final_products})
=======
    # ---- 🔍 Search ----
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(name_en__icontains=query) |
            Q(brand__icontains=query) |
            Q(brand_en__icontains=query)
        )

    # ---- ✅ Filters ----
    category = request.GET.get('category')
    skin_type = request.GET.get('skin_type')
    concern = request.GET.get('concern')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category:
        products = products.filter(category=category)

    if skin_type:
        products = products.filter(skin_types__icontains=skin_type)

    if concern:
        products = products.filter(concerns_targeted__icontains=concern)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # ---- 🔀 Sorting ----
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'popularity':
        products = products.order_by('-views')

    return render(request, 'mainpage/mainpage.html', {'products': products})
>>>>>>> cff05388b6d0d45544734473f1a1b5e8cf4766f6


#####################################################################

from difflib import SequenceMatcher
import re

close_letters = {
    'ض': ['1', 'ص', 'ش'],
    'ص': ['2', 'ض', 'ث', 'س'],
    'ث': ['3', 'ص', 'ق', 'ی'],
    'ق': ['4', 'ث', 'ف', 'ب'],
    'ف': ['5', 'ق', 'غ', 'ل'],
    'غ': ['5', '6', 'ف', 'ع', 'ا'],
    'ع': ['6', '7', 'غ', 'ه', 'ت'],
    'ه': ['7', 'ع', 'خ', 'ن'],
    'خ': ['8', 'ه', 'ح', 'م'],
    'ح': ['9', 'خ', 'ج', 'ک'],
    'ج': ['0', 'ح', 'چ', 'گ'],
    'چ': ['ج', 'پ', 'گ', 'ک', 'و'],
    'پ': ['چ', 'ن', 'و', 'د'],
    'ش': ['ض', 'س', 'ظ'],
    'س': ['ص', 'ش', 'ی', 'ط'],
    'ی': ['ث', 'س', 'ب', 'ب'],
    'ب': ['ق', 'ی', 'ل', 'ز'],
    'ل': ['ف', 'ب', 'ا', 'ر'],
    'ا': ['غ', 'ل', 'ت', 'ذ', 'آ'],
    'آ': ['غ', 'ل', 'ت', 'ذ', 'ا'],
    'ت': ['ع', 'ا', 'ن', 'د'],
    'ن': ['ه', 'ت', 'م', 'و', 'پ'],
    'م': ['خ', 'ن', 'ک', 'و'],
    'ک': ['ح', 'م', 'گ', 'چ'],
    'گ': ['ج', 'ک', 'چ'],
    'ظ': ['ش', 'ط'],
    'ط': ['س', 'ظ', 'ز', 'ژ'],
    'ژ': ['ی', 'ط', 'ز', 'ر'],
    'ز': ['ب', 'ژ', 'ر', 'ط'],
    'ر': ['ل', 'ز', 'ذ'],
    'ذ': ['ا', 'ر', 'د'],
    'د': ['ت', 'ذ', 'پ'],
    'و': ['م', 'چ', 'پ', 'ن'],
}

def similarity(user, db):
    t_length = len(db)
    each_letter = 100 / t_length
    rate = 0
    for i in range(min(len(user), len(db))):
        if user[i] == db[i]:
            rate += each_letter
        elif db[i] in close_letters:
            if user[i] in close_letters[db[i]]:
                rate += 0.8 * each_letter
    if len(user) != t_length and rate > 0.8:
        rate /= (abs(len(user) - t_length) ** 2 + 0.1)
    else:
        rate /= ((abs(len(user) - t_length) + 1) ** 3)
    if rate < 60:
        rate /= 2
    return rate / 100

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def search(request):
    full_query = request.GET.get('q').replace('\u200c', ' ')
    full_query = re.sub(r's+', ' ', full_query).strip()
    full_query = re.sub(r'[^a-zA-Zآ-ی0-9۰-۹\s]', '', full_query)
    query_words = full_query.lower().split()
    products = Product.objects.all()
    total_rating_average = sum([product.rating for product in products]) / len(products)
    results = []
    base_score = 5
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
        # score += 5 * bayesian_average(product, total_rating_average)
        product_name = product.name.lower().replace('\u200c', ' ')
        product_brand = product.brand.lower().replace('\u200c', ' ')

        base_score = 50
        for word in query_words:
            if word in product_name.split() or word in product_name.replace(' ', '') or product_name in word.replace(' ', ''):
                score += 10000
                # print('pdkwpe')
            elif word in product_brand:
                score += 8000
            else:
                base_score = 5
                for p_word in product_name.split():
                    # if similarity(word, p_word) > 0.75:
                    #     score += similarity(word, p_word) * 60
                    # else:
                    #     score += similarity(word, p_word) * 2
                    score += 10000 ** similarity(word, p_word)
                # brand_similarity = similar(word, product_brand)
                # print(brand_similarity)
                brand_similarity = similarity(word, product_brand)
                # print(brand_similarity)
                # if brand_similarity > 0.8:
                    # score += 20 * brand_similarity ** 2
                score += 8000 ** brand_similarity
                # score += similarity(word, product_brand) * (3.5 if brand_focus else 1.5)


        if score > base_score:
            # results.append((product, score))
            results.append((product, score * bayesian_average(product, total_rating_average)))
    results.sort(key=lambda x: x[1], reverse=True)

    for i in range(10):
        print(results[i])
    print(results[42])
    final_products = [r[0] for r in results][:500]

    # print(len(final_products))

    # print(similar('نیوآ', 'نیوا'))
    print(similarity('ضدجوش', 'ضدآفتاب'))
    print(similarity('ضداففاپب', 'اسنس مغذی'))
    print(similarity('ضداففاپب', 'ادیپیرن'))
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
    full_query = request.GET.get('q').replace('\u200c', ' ')
    if not full_query:
        return JsonResponse({'results': []})
    full_query = re.sub(r's+', ' ', full_query).strip()
    full_query = re.sub(r'[^a-zA-Zآ-ی0-9۰-۹\s]', '', full_query)
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
    for product in products:
        score = 0
        product_name = product.name.lower().replace('\u200c', ' ')
        product_brand = product.brand.lower().replace('\u200c', ' ')

        for word in query_words:
            if word in product_name.split() or word in product_name.replace(' ', '') or product_name in word.replace(' ', ''):
                score += 25
            elif word in product_brand:
                score += 35
            else:
                for p_word in product_name.split():   
                    score += similarity(word, p_word) * 10
                # brand_similarity = similar(word, product_brand)
                brand_similarity = similarity(word, product_brand)
                score += 20 * brand_similarity ** 2
                # score += similarity(word, product_brand) * (3.5 if brand_focus else 1.5)

        if score > 1:
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
            # 'id': product.id,
            'name': product.name,
            # 'brand': product.brand,
            # 'price': product.price,
            # 'image_url': product.image.url if product.image else '',
            # 'url': product.get_absolute_url() if hasattr(product, 'get_absolute_url') else ''
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

