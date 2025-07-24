from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment
from django.db.models import Q
from django.http import JsonResponse


def bayesian_average(product, total_rating_average):
    m = 50
    return (product.sales_count / (product.sales_count + m)) * product.rating + (m / (product.sales_count + m)) * total_rating_average

def filter(request, products):
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
    
def sort(request, products):
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'popularity':
        products = products.order_by('-views')

def mainpage(request):
    # Start with all products

    # ---- 🔍 Search ----
    products = search(request)

    # ---- ✅ Filters ----
    filter(request, products)

    # ---- 🔀 Sorting ----
    sort(request, products)

    skin_type = request.GET.get('skin_type')
    category = request.GET.get('category')
    context = {
        'products': products,
        'product_model': Product,
        'skin_type_se': skin_type,
        'category_se': category,
    }

    return render(request, 'mainpage/mainpage.html', context)



#####################################################################

from difflib import SequenceMatcher
from django.db.models import Case, When
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

from accounts.models import SearchHistory

def save_search(user, query):
    query = query.strip()
    if not query:
        return

    existing = SearchHistory.objects.filter(user=user, query=query).first()
    if existing:
        existing.save()
    else:
        SearchHistory.objects.create(user=user, query=query)

    recent = SearchHistory.objects.filter(user=user).order_by('-searched_at')
    if recent.count() > 30:
        for s in recent[30:]:
            s.delete()


def search(request, live=False):
    full_query = request.GET.get('q', '').replace('\u200c', ' ')
    full_query = re.sub(r's+', ' ', full_query).strip()
    full_query = re.sub(r'[^a-zA-Zآ-ی0-9۰-۹\s]', '', full_query)
    if not live:
        print(full_query, '+++++++++++++++++++++++++++++++')
        save_search(request.user, full_query)
    query_words = full_query.lower().split()
    products = Product.objects.all()
    total_rating_average = sum([product.rating for product in products]) / len(products)
    results = []
    base_score = 5

    if not full_query:
        for product in products:
            results.append((product.id, bayesian_average(product, total_rating_average)))
        results.sort(key=lambda x: x[1], reverse=True)
        selected_ids = [r[0] for r in results]
        preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
        return Product.objects.filter(id__in=selected_ids).order_by(preserved)
        final_products = [r[0] for r in results]
        return final_products
        return render(request, 'mainpage/mainpage.html', {'products': products})

    for product in products:
        score = 0
        product_name = product.name.lower().replace('\u200c', ' ')
        product_brand = product.brand.lower().replace('\u200c', ' ')

        base_score = 50
        for word in query_words:
            if word in product_name.split() or word in product_name.replace(' ', '') or product_name in word.replace(' ', ''):
                score += 10000
            elif word in product_brand:
                score += 8000
            else:
                base_score = 5
                for p_word in product_name.split():
                    score += 10000 ** similarity(word, p_word)
                brand_similarity = similarity(word, product_brand)
                score += 8000 ** brand_similarity

        if score > base_score:
            results.append((product.id, score * bayesian_average(product, total_rating_average)))
    results.sort(key=lambda x: x[1], reverse=True)
    selected_ids = [r[0] for r in results]
    preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
    return Product.objects.filter(id__in=selected_ids).order_by(preserved)
    final_products = [r[0] for r in results][:500]

    return final_products

    return render(request, 'mainpage/mainpage.html', {'products': final_products})

#####################################################################

from django.http import JsonResponse

def live_search(request):
    full_query = request.GET.get('q', '').replace('\u200c', ' ')
    print(full_query, '------')
    if not full_query:
        search_history = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')
        print(search_history)
        suggestions = [{'name': history.query} for history in search_history][:15]
    else:
        products = search(request, live=True)
        print(products)
        suggestions = []
        for product in products:
            if product.name not in suggestions:
                suggestions.append(product.name)
            if len(suggestions) > 15:
                break
        suggestions = list({'name': name} for name in suggestions)
    print(suggestions)
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

