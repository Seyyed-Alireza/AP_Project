from django.shortcuts import render, redirect, get_object_or_404
from mainpage.views import bayesian_average, similarity
from mainpage.models import Product
from .models import RoutinePlan
from django.contrib.auth.decorators import login_required
from mainpage.views import search

search_queries = {
    'oiliness': 'چربی زیاد چرب',
    'sensitivity': 'حساس حساسیت'
}

@login_required
def routine_generator(request):
    skin_scores = request.user.skinprofile.get_skin_scores()
    skin_scores.sort(key=lambda x: x[1], reverse=True)
    steps = []
    print(skin_scores)
    if skin_scores[0][0] == 'oiliness':
        steps.append({'order': 1, 'step_name': 'کاهش چربی', 'search_query': search_queries['oiliness']})
    if skin_scores[1][0] == 'sensitivity':
        steps.append({'order': 2, 'step_name': 'کاهش حساسیت', 'search_query': search_queries['sensitivity']})

    if not RoutinePlan.objects.filter(user=request.user).exists():
        RoutinePlan.objects.create(user=request.user, steps=steps)
    else:
        RoutinePlan.objects.filter(user=request.user).delete()
        RoutinePlan.objects.create(user=request.user, steps=steps)

    return redirect('profile')

def find_step_products(request):
    routine_plan = get_object_or_404(RoutinePlan, user=request.user)
    results = []
    for step in routine_plan.steps:
        step_products = search(request, search_query=step['search_query'], routine=True)
        results.append([step['step_name'], step_products])

    return results

import re
from django.db.models import Case, When
def routine_search(full_query):
    full_query = full_query.replace('\u200c', ' ')
    full_query = re.sub(r's+', ' ', full_query).strip()
    full_query = re.sub(r'[^a-zA-Zآ-ی0-9۰-۹\s]', '', full_query)
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

    NAME_BASE_SCORE = 12000
    BRAND_BASE_SCORE = 10000
    INGREDIENT_BASE_SCORE = 8000
    CONCERN_BASE_SCORE = 11000
    SKIN_TYPE_BASE_SCORE = 12000
    RATING_BASE_SCORE = 5000
    for product in products:
        score = 0
        product_name = product.name.lower().replace('\u200c', ' ')
        product_brand = product.brand.lower().replace('\u200c', ' ')
        base_score = 50
        for word in query_words:
            if similarity('پوست', word) >= 0.95:
                continue
            if word in product_name.split() or word in product_name.replace(' ', '') or product_name in word.replace(' ', ''):
                score += NAME_BASE_SCORE
            elif word in product_brand.split():
                score += BRAND_BASE_SCORE
            elif word in product.concerns_targeted:
                score += CONCERN_BASE_SCORE
            elif word in product.skin_types:
                score += SKIN_TYPE_BASE_SCORE
            else:
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
                if not name_similar and not brand_similar:
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

                if not ingredient_similar and not name_similar and not brand_similar:
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
    results = results[:10]
    selected_ids = [r[0] for r in results]
    preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
    return Product.objects.filter(id__in=selected_ids).order_by(preserved)

