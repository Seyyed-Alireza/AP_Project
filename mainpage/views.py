from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment
from django.db.models import Q
from django.http import JsonResponse


def bayesian_average(product, total_rating_average):
    m = 50
    return ((product.sales_count / (product.sales_count + m)) * product.rating + (m / (product.sales_count + m)) * total_rating_average) / 5

def filter(request, products):
    brand = request.GET.get('brand')
    category = request.GET.get('category')
    category_en = [c[0] for c in Product.CATEGORY_CHOICES]
    if category not in category_en:
        for cat in Product.CATEGORY_CHOICES:
            if cat[1] == category:
                category = cat[0]
                break
    skin_type = request.GET.get('skin_type')
    skin_types_en = [s[0] for s in Product.SKIN_TYPE_CHOICES]
    if skin_type not in skin_types_en:
        for sk in Product.SKIN_TYPE_CHOICES:
            if sk[1] == skin_type:
                skin_type = sk[0]
                break
    concern = request.GET.get('concern')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if brand:
        products = products.filter(brand=brand)

    if category:
        products = products.filter(category=category)

    if skin_type:
        products = products.filter(skin_types__icontains=skin_type)

    # if concern:
    #     products = products.filter(concerns_targeted__icontains=concern)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    return products
    
def sort(request, products):
    sort_by = request.GET.get('sort_by')
    has_sort = False
    if sort_by == 'price_low':
        has_sort = True
        products = products.order_by('price')
    elif sort_by == 'price_high':
        has_sort = True
        products = products.order_by('-price')
    elif sort_by == 'rating':
        has_sort = True
        products = products.order_by('-rating')
    elif sort_by == 'popularity':
        has_sort = True
        products = products.order_by('-views')
    return products, has_sort

def mainpage(request):

    # Start with all products
    products = Product.objects.all()

    # ---- ✅ Filters ----
    products = filter(request, products)

    # ---- 🔀 Sorting ----
    products, has_sort = sort(request, products)
    skin_type = request.GET.get('skin_type')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    sort_by = request.GET.get('sort_by')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    filters = [brand, category, skin_type, min_price, max_price, sort_by]
    for_cache = ''.join([str(x) for x in filters if x != None])

    # ---- 🔍 Search ----
    products = search(request, products, for_cache, has_sort)

    context = {
        'products': products,
        'product_model': Product,
        'skin_type_se': skin_type,
        'category_se': category,
        'brand_se': brand
    }

    return render(request, 'mainpage/mainpage.html', context)

def more_products(request):
    q = request.GET.get('query')
    query_words = q.split()
    q_objects = Q()
    for word in query_words:
        q_objects |= Q(name__icontains=word)
    products = Product.objects.filter(q_objects)

    # ---- ✅ Filters ----
    products = filter(request, products)

    # ---- 🔀 Sorting ----
    products, has_sort = sort(request, products)

    skin_type = request.GET.get('skin_type')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    sort_by = request.GET.get('sort_by')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    filters = [brand, category, skin_type, min_price, max_price, sort_by]
    for_cache = ''.join([str(x) for x in filters if x != None])
    products = search(request, products, for_cache, has_sorted=has_sort, for_more=True)
    from routine.views import routine_search
    # products = routine_search(request, search_query=q)

    context = {
        'products': products,
        'product_model': Product,
        'skin_type_se': skin_type,
        'category_se': category,
        'brand_se': brand
    }

    return render(request, 'mainpage/more_products.html', context)



from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework import generics

class MainpageAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        print('--------------------start----------------------')
        products = Product.objects.all()
        products = filter(self.request, products)
        products, has_sort = sort(self.request, products)
        skin_type = self.request.GET.get('skin_type')
        category = self.request.GET.get('category')
        brand = self.request.GET.get('brand')
        sort_by = self.request.GET.get('sort_by')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        user_in = self.request.GET.get('user_id')
        filters = [brand, category, skin_type, min_price, max_price, sort_by]
        for_cache = ''.join([str(x) for x in filters if x is not None])

        products_with_reasons = search(self.request, products, for_cache, has_sort, api=True, user_in=user_in)

        products_only = [prod for prod, reason in products_with_reasons]

        self.products_reasons = {prod.id: reason for prod, reason in products_with_reasons}

        return products_only

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            data_with_reasons = [
                {**serializer.data[i], "reason": self.products_reasons[queryset[i].id]}
                for i in range(len(queryset))
            ]

            all_products = Product.objects.all()
            brands = all_products.values_list('brand', flat=True).distinct()
            categories = [category[1] for category in Product.CATEGORY_CHOICES]
            skin_types = ['مختلط', 'خشک', 'چرب', 'حساس', 'نرمال']

            return Response({
                'products': data_with_reasons,
                'brands': list(brands),
                'categories': list(categories),
                'skin_types': list(skin_types),
            })
        except Exception as e:
            import traceback; traceback.print_exc()
            return Response({"error": str(e)}, status=500)

    
class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"


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
    rate = 0
    user = user.replace('آ', 'ا')
    db = db.replace('آ', 'ا')
    db_len = len(db)
    us_len = len(user)
    each_letter = 100 / db_len
    if us_len != db_len and (db in user or user in db):
        rate = 100
        rate - 5 * abs(us_len - db_len)
    for i in range(min(us_len, len(db))):
        if user[i] == db[i]:
            rate += each_letter
        elif db[i] in close_letters:
            if user[i] in close_letters[db[i]]:
                rate += 0.8 * each_letter
            else:
                rate += 0.1 * each_letter

    if us_len != db_len and rate > 0.8:
        rate /= (abs(us_len - db_len) ** 2 + 0.1)
    else:
        rate /= ((abs(us_len - db_len) + 1) ** 3)
    if rate < 45:
        rate /= 3
    elif rate < 65:
        rate /= (67 - rate)

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

from django.contrib.auth import get_user_model

User = get_user_model()


import pandas as pd

def get_similar_users(current_skin_types):
    if isinstance(current_skin_types, str):
        current_skin_types = [current_skin_types]

    fields = [
        f.name for f in SkinProfile._meta.get_fields()
        if f.concrete and f.name not in ('completed_at', 'quiz_skipped')
    ]

    fields += ['user__id']
    all_profiles_panda = pd.DataFrame(list(SkinProfile.objects.select_related('user').filter(skin_type__isnull=False).values(*fields)))
    # print(all_profiles_panda.to_string())

    mask = all_profiles_panda['skin_type'].apply(lambda x: any(st in x for st in current_skin_types))
    similar_user_ids = all_profiles_panda.loc[mask, 'user__id'].head(20).tolist()
    # print(request.user.username)

    return User.objects.filter(id__in=similar_user_ids)

def is_subset(list1, list2):
    return all(item in list2 for item in list1)

def both_subset(list1, list2):
    return set(list1).issubset(set(list2)) or set(list2).issubset(set(list1))

from quiz.models import SkinProfile
from accounts.models import ProductSearchHistory, ProductPurchaseHistory
from django.core.cache import cache
import hashlib
from django.db.models import Avg
import time
from mainpage.models import Comment

def search(request, products, for_cache, has_sorted, live=False, routine=False, search_query=None, for_more=False, api=False, user_in=None):
    start = time.time()
    if not routine:
        full_query = request.GET.get('q', '').replace('\u200c', ' ')
        if not live and request.user.is_authenticated:
            save_search(request.user, full_query)
    else:
        full_query = search_query
    full_query = re.sub(r's+', ' ', full_query).strip()
    full_query = re.sub(r'[^a-zA-Zآ-ی0-9۰-۹\s]', '', full_query)

    raw_key = f"{request.user.id}:{full_query}" if request.user.is_authenticated else f'{full_query}'
    raw_key += for_cache
    cache_key = "search:" + hashlib.md5(raw_key.encode()).hexdigest()

    cached_ids = cache.get(cache_key)
    # if cached_ids:
    #     ids = list(cached_ids.keys())
    #     preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(ids)])
    #     print(time.time() - start)
    #     products = Product.objects.filter(id__in=ids).order_by(preserved)
    #     products = [[prod, cached_ids[prod.id]] for prod in products]
    #     return products

    query_words = full_query.lower().split()
    if not for_more:
        q_objects = Q()
        for word in query_words:
            q_objects |= Q(name__icontains=word) | Q(brand__icontains=word) | Q(description__icontains=word)

        products_backup = products

        products = products.filter(q_objects)
        if len(products) <= 15 and not for_cache:
            products = products_backup

        if has_sorted:
            return [[product, 'طبق مرتب سازی'] for product in products]
    total_rating_average = cache.get(f'total_rating_average{cache_key}')
    if not total_rating_average or not isinstance(total_rating_average, (int, float)):
        total_rating_average = Product.objects.aggregate(avg=Avg('rating'))['avg'] or 2.5
        cache.set(key=f'total_rating_average{cache_key}', value=total_rating_average, timeout=86400)
    NAME_BASE_SCORE = 15000
    BRAND_BASE_SCORE = 9000
    INGREDIENT_BASE_SCORE = 4500
    CONCERN_BASE_SCORE = 5000
    SKIN_TYPE_BASE_SCORE = 5000
    RATING_BASE_SCORE = 4000
    SIMILAR_PURCHASE_BASE_SCORE = 800
    SIMILAR_LIKE_BASE_SCORE = 500
    SIMILAR_CART_BASE_SCORE = 400
    SIMILAR_VIEW_BASE_SCORE = 200
    SIMILAR_WISH_BASE_SCORE = 250
    SIMILAR_COMMENT_BASE_SCORE = 150
    DEFAULT_REASON = 'شاید بپسندید'
    results = []
    base_score = 5

    if api:
        if user_in:
            try:
                user = User.objects.get(id=user_in)
                user_in = True
                print('user -->', user)
                similar_users = get_similar_users(user.skinprofile.skin_type)
            except:
                similar_users = []
                user_in = False
                user = request.user
        else:
            user = request.user
            similar_users = []
    else:
        user = request.user
        user_in = False
        if user.is_authenticated and hasattr(user, 'skinprofile'):
            similar_users = get_similar_users(user.skinprofile.skin_type)
            user_in = True
        else:
            similar_users = []

    purchases = set(
        ProductPurchaseHistory.objects.filter(
            user__in=similar_users,
        ).values_list('user_id', 'product_id')
    )

    interactions = set(
        ProductSearchHistory.objects.filter(
            user__in=similar_users
        ).values_list('user_id', 'product_id', 'interaction_type')
    )

    comments = set(
        Comment.objects.filter(
            user__in=similar_users
        ).values_list('user_id', 'product_id')
    )

    print(similar_users, '----------------')
    if not full_query:
        if user_in:
            if user.skinprofile.quiz_completed:
                for product in products:
                    score = 0
                    reason = DEFAULT_REASON
                    for similar_user in similar_users:
                        if (similar_user.id, product.id) in purchases:
                            score += SIMILAR_PURCHASE_BASE_SCORE
                            reason = 'کابران مشابه خریده‌اند'
                        elif (similar_user.id, product.id, 'cart') in interactions:
                            score += SIMILAR_CART_BASE_SCORE
                        elif (similar_user.id, product.id, 'wish') in interactions:
                            score += SIMILAR_WISH_BASE_SCORE
                        elif (similar_user.id, product.id, 'like') in interactions:
                            score += SIMILAR_LIKE_BASE_SCORE
                            reason = 'کابران مشابه علاقه داشتند'
                        elif (similar_user.id, product.id, 'view') in interactions:
                            score += SIMILAR_VIEW_BASE_SCORE
                            reason = 'کابران مشابه بازدید کردند'
                        elif (similar_user.id, product.id) in comments:
                            score += SIMILAR_COMMENT_BASE_SCORE
                    concern_similar = False
                    type_similar = False
                    skin_scores = SkinProfile.get_skin_scores_for_search(user.skinprofile)
                    skin_scores.sort(key=lambda x: x[1], reverse=True)
                    for skin_score in skin_scores:
                        if skin_score[1] > 10:
                            for concern_targeted in product.concerns_targeted:
                                if both_subset(skin_score[0].split(), concern_targeted.split()):
                                    concern_similar = True
                                    score += CONCERN_BASE_SCORE
                                    if reason == DEFAULT_REASON:
                                        reason = 'مناسب مشکل پوست شما'
                                    break
                            if concern_similar:
                                break
                    for s_t in user.skinprofile.skin_type:
                        if s_t in product.skin_types:
                            type_similar = True
                            score += SKIN_TYPE_BASE_SCORE
                            if reason == DEFAULT_REASON:
                                reason = 'مناسب پوست شما'
                            break
                    results.append((product.id, score + RATING_BASE_SCORE ** bayesian_average(product, total_rating_average), reason))
            else:
                results = [(product.id, bayesian_average(product, total_rating_average), DEFAULT_REASON) for product in products]
        else:
            results = [(product.id, bayesian_average(product, total_rating_average), DEFAULT_REASON) for product in products]
        results.sort(key=lambda x: x[1], reverse=True)
        id_reason = {r[0]: r[2] for r in results}
        selected_ids = list(id_reason.keys())
        cache.set(cache_key, selected_ids, timeout=86400)
        preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
        print(time.time() - start)
        products = list(Product.objects.filter(id__in=selected_ids).order_by(preserved))
        products_for_cache = {prod.id: id_reason[prod.id] for prod in products}
        cache.set(cache_key, products_for_cache, timeout=86400)
        products = [[prod, id_reason[prod.id]] for prod in products]
        return products
    
    for product in products:
        reason = DEFAULT_REASON
        score = 0
        product_name = product.name.lower().replace('\u200c', ' ')
        product_brand = product.brand.lower().replace('\u200c', ' ')

        base_score = 50
        for word in query_words:
            if similarity('پوست', word) >= 0.95:
                continue
            name_similar = False
            brand_similar = False
            ingredient_similar = False
            type_similar = False
            concern_similar = False

            if product_name in full_query or word in product_name.split() or word in product_name.replace(' ', '') or product_name in word.replace(' ', ''):
                name_similar = True
                score += NAME_BASE_SCORE
                reason = 'مطابق با چیزی که جستجو کردید'
            else:
                for p_word in product_name.split():
                        s = similarity(word, p_word)
                        if s > 0.85:
                            name_similar = True
                            score += NAME_BASE_SCORE
                            reason = 'مطابق با چیزی که جستجو کردید'
                            break
            
            if both_subset([word], product_brand.split()):
                brand_similar = True
                score += BRAND_BASE_SCORE

            for skin_type in product.skin_types:
                if both_subset(skin_type.split(), [word]):
                    type_similar = True
                    score += SKIN_TYPE_BASE_SCORE if not name_similar else SKIN_TYPE_BASE_SCORE / 10
                    break
            if user_in:
                if user.skinprofile.quiz_completed and not type_similar:
                    for s_t in user.skinprofile.skin_type:
                        if s_t in product.skin_types:
                            type_similar = True
                            reason = 'مناسب پوست شما'
                            score += SKIN_TYPE_BASE_SCORE if not name_similar else SKIN_TYPE_BASE_SCORE / 10
                            break

            for concern_targeted in product.concerns_targeted:
                if both_subset(concern_targeted.split(), [word]):
                    concern_similar = True
                    reason = 'مناسب مشکل پوست شما'
                    score += CONCERN_BASE_SCORE if not name_similar else CONCERN_BASE_SCORE / 10
                    break
            if user_in:
                if user.skinprofile.quiz_completed and not concern_similar:
                    skin_scores = SkinProfile.get_skin_scores_for_search(user.skinprofile)
                    skin_scores.sort(key=lambda x:x[1], reverse=True)
                    for skin_score in skin_scores:
                        if skin_score[1] > 10:
                            for concern_targeted in product.concerns_targeted:
                                if both_subset(skin_score[0].split() in concern_targeted.split()):
                                    concern_similar = True
                                    score += CONCERN_BASE_SCORE if not name_similar else CONCERN_BASE_SCORE / 10
                                    break
                            if concern_similar:
                                break

            if not any([name_similar, brand_similar, concern_similar, type_similar, ingredient_similar]):
                base_score = 5
                name_similarity = 0
                name_counter = 0
                for p_word in product_name.split():
                    s = similarity(word, p_word)
                    if s > 90:
                        name_similarity = NAME_BASE_SCORE
                        name_counter = 1
                        break
                    elif s < 30:
                        score -= NAME_BASE_SCORE
                    name_similarity += NAME_BASE_SCORE ** similarity(word, p_word)
                    name_counter += 1
                name_similarity /= name_counter
                name_similar = True if name_similarity > 0.85 * NAME_BASE_SCORE else False
                # score += name_similarity
                brand_similarity = BRAND_BASE_SCORE ** similarity(word, product_brand)
                brand_similar = True if brand_similarity > 0.85 * BRAND_BASE_SCORE else False
                # score += brand_similarity

                if not concern_similar and not name_similar and not brand_similar:
                    concern_counter = 0
                    concern_similarity = 0
                    found = False
                    for concern in product.concerns_targeted:
                        if word in concern.split():
                            concern_similarity = CONCERN_BASE_SCORE
                            concern_counter = 1
                            break
                        for p_concern in concern.split():
                            c = similarity(word, p_concern)
                            if c > 0.9:
                                concern_similarity = CONCERN_BASE_SCORE
                                concern_counter = 1
                                found = True
                                break
                            concern_similarity += CONCERN_BASE_SCORE ** c
                            concern_counter += 1
                        if found:
                            break
                    concern_similarity /= concern_counter
                    concern_similar = True if concern_similarity > 0.85 * CONCERN_BASE_SCORE else False
                    # score += concern_similarity
                    # score += max(name_similarity, brand_similarity, ingredient_similarity, concern_similarity)
                else:
                    concern_similar = False
                    concern_similarity = 0
                    
                if not concern_similar and not ingredient_similar and not name_similar and not brand_similar:
                    type_counter = 0
                    type_similarity = 0
                    if word in product.get_skin_types_fa():
                        type_similarity = SKIN_TYPE_BASE_SCORE
                        type_counter = 1
                    else:
                        for skin_type in product.get_skin_types_fa():
                            st = similarity(word, skin_type)
                            if st > 0.9:
                                type_similarity = SKIN_TYPE_BASE_SCORE
                                type_counter = 1
                                break
                            type_similarity += SKIN_TYPE_BASE_SCORE ** st
                            type_counter += 1
                    if type_counter == 0:
                        type_counter = 1
                    type_similarity /= type_counter
                    type_similar = True if type_similarity > 0.85 * SKIN_TYPE_BASE_SCORE else False       
                else:
                    type_similar = False
                    type_similarity = 0

                if not name_similar and not brand_similar and not type_similar and not concern_similar:
                    ingredient_counter = 0
                    ingredient_similarity = 0
                    found = False
                    for ingredient in product.ingredients:
                        if word in ingredient.split():
                            ingredient_similarity = INGREDIENT_BASE_SCORE
                            ingredient_counter = 1
                            break
                        for p_ingredient in ingredient.split():
                            i = similarity(word, p_ingredient)
                            if i > 0.9:
                                ingredient_similarity = INGREDIENT_BASE_SCORE
                                ingredient_counter = 1
                                found = True
                                break
                            ingredient_similarity += INGREDIENT_BASE_SCORE ** i
                            ingredient_counter += 1
                        if found:
                            break
                    ingredient_similarity /= ingredient_counter
                    # score += ingredient_similarity
                    ingredient_similar = True if ingredient_similarity > 0.85 * INGREDIENT_BASE_SCORE else False
                else:
                    ingredient_similar = False
                    ingredient_similarity = 0

                if type_similar:
                    score += type_similarity
                else:
                    n = name_similarity / NAME_BASE_SCORE
                    b = brand_similarity / BRAND_BASE_SCORE
                    i = ingredient_similarity / INGREDIENT_BASE_SCORE
                    c = concern_similarity / CONCERN_BASE_SCORE
                    t = type_similarity / SKIN_TYPE_BASE_SCORE
                    if n > max(b, i, c, t):
                        score += name_similarity
                    elif b > max(i, c, t):
                        score += brand_similarity
                    elif i > max(c, t):
                        score += ingredient_similarity
                    elif c > t:
                        score += concern_similarity
                    else:
                        score += type_similarity



        # if score > base_score + 1:
        results.append((product.id, score + RATING_BASE_SCORE ** bayesian_average(product, total_rating_average), reason))
            
    results.sort(key=lambda x: x[1], reverse=True)
    if routine:
        results = results[:10]
    id_reason = {r[0]: r[2] for r in results}
    selected_ids = list(id_reason.keys())
    preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
    print(time.time() - start)
    products = list(Product.objects.filter(id__in=selected_ids).order_by(preserved))
    products_for_cache = {prod.id: id_reason[prod.id] for prod in products}
    cache.set(cache_key, products_for_cache, timeout=86400)
    products = [[prod, id_reason[prod.id]] for prod in products]
    return products
    
#####################################################################

from django.http import JsonResponse

def live_search(request):
    full_query = request.GET.get('q', '').replace('\u200c', ' ')
    if not full_query and request.user.is_authenticated:
        search_history = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')
        suggestions = [{'name': history.query} for history in search_history][:15]
    else:
        if not full_query:
            return JsonResponse('')
        query_words = full_query.split()
        q_objects = Q()
        for word in query_words:
            q_objects |= Q(name__icontains=word) | Q(brand__icontains=word)
        products = search(request, live=True, for_cache='for_save', has_sorted=False, products=Product.objects.filter(q_objects))
        products = [i[0] for i in products]
        suggestions = []
        for product in products:
            if product.name not in suggestions:
                suggestions.append(product.name)
            if len(suggestions) > 15:
                break
        suggestions = list({'name': name} for name in suggestions)
    return JsonResponse({'results': suggestions})

#######################################################################

from accounts.models import ProductSearchHistory
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    user = request.user
    if user.is_authenticated and not ProductSearchHistory.objects.filter(user=user, product=product, interaction_type='view').exists():
        ProductSearchHistory.objects.create(user=user, product=product, interaction_type='view')
        product.views += 1
    elif not user.is_authenticated:
        product.views += 1
    product.save(update_fields=['views'])

    comments = product.comments.all().order_by('-created_at')

    before_commented = False
    if user.is_authenticated:
        before_commented = product.comments.filter(user=user).exists()

    if request.method == 'POST':
        if not user.is_authenticated:
            return redirect('mainpage:login')

        text = request.POST.get('text')
        rating = request.POST.get('rating')

        if text and rating and rating.isdigit() and 1 <= int(rating) <= 5:
            Comment.objects.create(
                product=product,
                user=user,
                text=text,
                rating=int(rating)
            )
            return redirect('mainpage:product_detail', pk=pk)

    liked = None
    if user.is_authenticated and ProductSearchHistory.objects.filter(user=request.user, product=product, interaction_type='like').exists():
        liked = True
    else:
        liked = False
    return render(request, 'mainpage/product_detail.html', {
        'product': product,
        'comments': comments,
        'commented_before': before_commented,
        'liked': liked
    })

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def like_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        like, created = ProductSearchHistory.objects.get_or_create(user=request.user, product=product, interaction_type=ProductSearchHistory.INTERACTION_TYPES[1][0])
        if not created:
            like.delete()
            product.likes = max(0, product.likes - 1)
        else:
            product.likes += 1
        product.save(update_fields=['likes'])
        return JsonResponse({'success': True, 'likes': product.likes})
    return JsonResponse({'success': False}, status=400)
