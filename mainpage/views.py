from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment
from django.db.models import Q
from django.http import JsonResponse


def bayesian_average(product, total_rating_average):
    m = 50
    return ((product.sales_count / (product.sales_count + m)) * product.rating + (m / (product.sales_count + m)) * total_rating_average) / 5

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

    return products
    
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
    return products

def mainpage(request):
    # Start with all products

    # ---- 🔍 Search ----
    products = search(request)

    # ---- ✅ Filters ----
    products = filter(request, products)

    # ---- 🔀 Sorting ----
    products = sort(request, products)

    skin_type = request.GET.get('skin_type')
    category = request.GET.get('category')
    context = {
        'products': products,
        'product_model': Product,
        'skin_type_se': skin_type,
        'category_se': category,
    }

    return render(request, 'mainpage/mainpage.html', context)


from rest_framework import generics
from .serializers import ProductSerializer
class MainpageAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        products = search(self.request)
        filter(self.request, products)
        sort(self.request, products)
        return products[:20]

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
        if user[i] == db[i] or user[i] in ('ا', 'آ'):
            rate += each_letter
        elif db[i] in close_letters:
            if user[i] in close_letters[db[i]]:
                rate += 0.8 * each_letter
    if len(user) != t_length and rate > 0.8:
        rate /= (abs(len(user) - t_length) ** 2 + 0.1)
    else:
        rate /= ((abs(len(user) - t_length) + 1) ** 3)
    if rate < 45:
        rate = 0
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

def get_similar_users(current_skin_types):
    if isinstance(current_skin_types, str):
        current_skin_types = [current_skin_types]

    all_profiles = SkinProfile.objects.select_related('user').filter(skin_type__isnull=False)

    similar_users = []
    for profile in all_profiles:
        if any(st in profile.skin_type for st in current_skin_types):
            similar_users.append(profile.user)
            if len(similar_users) >= 20:
                break
    return similar_users

    

from quiz.models import SkinProfile
from accounts.models import ProductSearchHistory

def search(request, live=False):
    full_query = request.GET.get('q', '').replace('\u200c', ' ')
    full_query = re.sub(r's+', ' ', full_query).strip()
    full_query = re.sub(r'[^a-zA-Zآ-ی0-9۰-۹\s]', '', full_query)
    if not live and request.user.is_authenticated:
        save_search(request.user, full_query)
    query_words = full_query.lower().split()
    products = Product.objects.all()
    total_rating_average = sum([product.rating for product in products]) / len(products)
    NAME_BASE_SCORE = 12000
    BRAND_BASE_SCORE = 10000
    INGREDIENT_BASE_SCORE = 8000
    CONCERN_BASE_SCORE = 10000
    SKIN_TYPE_BASE_SCORE = 10000
    RATING_BASE_SCORE = 5000
    results = []
    base_score = 5

    user = request.user
    similar_users = get_similar_users(user.skinprofile.skin_type)
    if not full_query:
        purchases = ProductSearchHistory.objects.filter(
            user__in=similar_users,
            interaction_type='purchase'
        ).values_list('user_id', 'product_id')
        purchases = set(purchases)

        if user.skinprofile.quiz_completed:
            for product in products:
                score = 0
                for similar_user in similar_users:
                    if (similar_user.id, product.id) in purchases:
                        score += 1000000

                concern_similar = False
                type_similar = False
                skin_scores = SkinProfile.get_skin_scores_for_search(user.skinprofile)
                for skin_score in skin_scores:
                    if skin_score[1] > 10:
                        for concern_targeted in product.concerns_targeted:
                            if skin_score[0] in concern_targeted or concern_targeted in skin_score[0]:
                                concern_similar = True
                                score += CONCERN_BASE_SCORE
                                break
                        if concern_similar:
                            break
                for s_t in user.skinprofile.skin_type:
                    if s_t in product.skin_types:
                        type_similar = True
                        score += SKIN_TYPE_BASE_SCORE
                        break
                results.append((product.id, score + RATING_BASE_SCORE ** bayesian_average(product, total_rating_average)))
        else:
            results.append((product.id, bayesian_average(product, total_rating_average)) for product in products)
        results.sort(key=lambda x: x[1], reverse=True)
        selected_ids = [r[0] for r in results]
        preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
        return Product.objects.filter(id__in=selected_ids).order_by(preserved)

    for product in products:
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
            
            if product_brand in full_query or word in product_brand.split():
                brand_similar = True
                score += BRAND_BASE_SCORE

            for skin_type in product.skin_types:
                if skin_type in full_query or word in skin_type:
                    type_similar = True
                    score += SKIN_TYPE_BASE_SCORE
                    break
            if user.skinprofile.quiz_completed and not type_similar:
                for s_t in user.skinprofile.skin_type:
                    if s_t in product.skin_types:
                        type_similar = True
                        score += SKIN_TYPE_BASE_SCORE
                        break

            for concern_targeted in product.concerns_targeted:
                if concern_targeted in full_query or word in concern_targeted:
                    concern_similar = True
                    score += CONCERN_BASE_SCORE
                    break
            if user.skinprofile.quiz_completed and not concern_similar:
                skin_scores = SkinProfile.get_skin_scores_for_search()
                for skin_score in skin_scores:
                    if skin_score[1] > 10:
                        for concern_targeted in product.concerns_targeted:
                            if skin_score[0] in concern_targeted or concern_targeted in skin_score[0]:
                                concern_similar = True
                                score += CONCERN_BASE_SCORE
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
                    if product.price == 4584908:
                        print(concern_similarity, '----------')
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



        if score > base_score + 1:
            results.append((product.id, score + RATING_BASE_SCORE ** bayesian_average(product, total_rating_average)))
            
    results.sort(key=lambda x: x[1], reverse=True)
    print(results[0][1])
    print(results[1][1])
    selected_ids = [r[0] for r in results]
    preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
    return Product.objects.filter(id__in=selected_ids).order_by(preserved)
    
#####################################################################

from django.http import JsonResponse

def live_search(request):
    full_query = request.GET.get('q', '').replace('\u200c', ' ')
    if not full_query and request.user.is_authenticated:
        search_history = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')
        suggestions = [{'name': history.query} for history in search_history][:15]
    else:
        products = search(request, live=True)
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
            return redirect('login')

        text = request.POST.get('text')
        rating = request.POST.get('rating')

        if text and rating and rating.isdigit() and 1 <= int(rating) <= 5:
            Comment.objects.create(
                product=product,
                user=user,
                text=text,
                rating=int(rating)
            )
            return redirect('product_detail', pk=pk)

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
