from django.shortcuts import render, redirect, get_object_or_404
from mainpage.views import bayesian_average, similarity
from mainpage.models import Product
from .models import RoutinePlan
from django.contrib.auth.decorators import login_required
from mainpage.views import search
from quiz.models import SkinProfile
from accounts.models import ProductSearchHistory

SEARCH_QUERIES = {
    'oiliness': 'چربی زیاد چرب',
    'sensitivity': 'حساس حساسیت',
    'acne': 'اکنه جوش',
    'hydration': 'آبرسان آب‌رسان',
    'dryness': 'خشکی خشک مرطوب',
    'redness': 'قرمزی التهاب',
    'elasticity': 'کشسان ارتجاعی'
}

STEP_NAMES = {
    'oiliness': 'کنترل چربی پوست',
    'sensitivity': 'کاهش حساسیت',
    'acne': 'درمان جوش و آکنه',
    'hydration': 'آبرسانی عمیق',
    'dryness': 'رفع خشکی پوست',
    'redness': 'کاهش قرمزی و التهاب',
    'elasticity': 'افزایش استحکام و کشسانی'
}

STEP_DESCRIPTIONS = {
    "cleanser": "پاکسازی اولین و مهم‌ترین گام مراقبت پوسته. باعث حذف آلودگی، چربی اضافه و سلول‌های مرده میشه. اگر انجام نشه، منافذ بسته میشن و زمینه برای جوش، التهاب و کدر شدن پوست فراهم میشه.",
    "toner": "تونر pH پوست را متعادل می‌کند و پوست را برای جذب بهتر محصولات بعدی آماده می‌سازد. حذف این مرحله ممکن است کارایی سرم و کرم‌ها را کاهش دهد.",
    "serum": "سرم حاوی مواد فعال است که مشکلات خاص پوست مانند لک یا چین‌وچروک را هدف قرار می‌دهد. اگر استفاده نشود، روند بهبود پوست کندتر خواهد بود.",
    "moisturizer": "مرطوب‌کننده رطوبت پوست را حفظ کرده و مانع از خشکی و حساسیت می‌شود. حذف این مرحله باعث کم‌آبی پوست و ایجاد خطوط ریز می‌گردد.",
    "sunscreen": "ضدآفتاب از پوست در برابر اشعه‌های مضر خورشید محافظت می‌کند و از پیری زودرس و سرطان پوست جلوگیری می‌کند. عدم استفاده باعث آسیب جدی به پوست می‌شود.",
    "hydrating Mask": "ماسک آبرسان رطوبت عمیق به پوست می‌رساند و ظاهر آن را شاداب می‌کند. حذف این مرحله ممکن است باعث خستگی و کدری پوست شود."
}

PROBLEM_TO_STEP = {
    "acne": {
        # "Cleanser": "پاکسازی روزانه چربی و آلودگی رو از بین می‌بره و جلوی انسداد منافذ رو می‌گیره. اگر این مرحله رو حذف کنی، جوش‌ها بیشتر و التهاب پوستت شدیدتر میشه.",
        "Serum": "سرم ضدجوش با مواد فعال مثل سالیسیلیک اسید یا نیاسینامید باعث کاهش التهاب و پیشگیری از ایجاد جوش جدید میشه. حذفش یعنی جوش‌ها دیرتر خوب میشن.",
        "Sunscreen": "ضدآفتاب از لک و تیره شدن جای جوش جلوگیری می‌کنه. بدون اون جای جوش‌ها پررنگ‌تر و موندگارتر میشه."
    },
    "oiliness": {
        # "Cleanser": "پاکسازی پوست چرب جلوی برق افتادن و انسداد منافذ رو می‌گیره. حذفش باعث افزایش جوش و ظاهر براق پوست میشه.",
        "Toner": "تونر متعادل‌کننده چربی پوست رو تنظیم می‌کنه. بدونش پوستت سریع‌تر چرب میشه.",
        "Serum": "سرم سبک با کنترل چربی کمک می‌کنه منافذ کوچیک‌تر بشن. حذفش یعنی کنترل کمتر روی چربی پوست."
    },
    "dryness": {
        # "Cleanser": "پاک‌کننده ملایم آلودگی رو می‌بره بدون اینکه پوست رو خشک‌تر کنه. اگه نباشه پوستت پوسته‌پوسته و خشن میشه.",
        "Serum": "سرم آبرسان لایه‌های عمقی پوست رو هیدراته می‌کنه. حذفش یعنی خشکی ادامه پیدا می‌کنه.",
        "Moisturizer": "مرطوب‌کننده رطوبت رو توی پوست قفل می‌کنه. بدونش خشکی بدتر و پوست حساس‌تر میشه."
    },
    "sensitivity": {
        # "Cleanser": "پاک‌کننده ملایم بدون تحریک پوست. اگر حذف بشه آلودگی می‌مونه و تحریک‌پذیری بیشتر میشه.",
        "Serum": "سرم آرام‌بخش قرمزی و التهاب رو کم می‌کنه. حذفش یعنی پوستت زودتر تحریک میشه.",
        "Moisturizer": "مرطوب‌کننده سد محافظ پوست رو قوی می‌کنه. بدونش پوستت نسبت به محرک‌ها آسیب‌پذیرتر میشه."
    },
    "hydration": {
        # "Cleanser": "پاک‌کننده ملایم اجازه میده محصولات آبرسان بهتر جذب بشن. حذفش یعنی آبرسانی کمتر.",
        "Hydrating Mask": "ماسک آبرسان فوراً رطوبت از دست رفته رو جبران می‌کنه. حذفش یعنی پوستت زودتر دهیدراته میشه.",
        "Moisturizer": "مرطوب‌کننده رطوبت رو حفظ می‌کنه. بدونش خشکی و کدری بیشتر میشه."
    },
    "elasticity": {
        # "Cleanser": "پاکسازی قبل از محصولات ضدپیری باعث جذب بهترشون میشه. حذفش یعنی تاثیر کمتر محصولات.",
        "Serum": "سرم تقویتی کلاژن‌سازی رو تحریک می‌کنه. بدونش افتادگی زودتر ایجاد میشه.",
        "Moisturizer": "مرطوب‌کننده باعث نرمی و جلوگیری از خطوط میشه. حذفش یعنی چین‌وچروک زودتر ظاهر میشه.",
        "Sunscreen": "ضدآفتاب از تخریب کلاژن جلوگیری می‌کنه. بدونش افتادگی سریع‌تر میاد."
    },
    "redness": {
        # "Cleanser": "پاک‌کننده ملایم التهاب رو بدتر نمی‌کنه و آلودگی رو می‌بره. بدونش قرمزی موندگار میشه.",
        "Serum": "سرم ضدالتهاب قرمزی رو کاهش میده. حذفش یعنی تحریک و قرمزی بیشتر.",
        "Moisturizer": "مرطوب‌کننده سد پوستی رو ترمیم می‌کنه. بدونش پوست آسیب‌پذیرتر میشه.",
        "Sunscreen": "ضدآفتاب مانع تشدید قرمزی توسط نور خورشید میشه. حذفش یعنی قرمزی و لکه‌های دائم."
    }
}

PROBLEM_TO_STEPS = {
    "acne": {
        "تونر": {
            "search_query": "تونر آکنه",
            'key_query': 'تونر',
            "why": "چربی پوست را متعادل کرده و منافذ را کوچک می‌کند.",
            "consequence": "بدون تونر، پوست چرب‌تر شده و احتمال جوش افزایش می‌یابد."
        },
        "سرم": {
            "search_query": "سرم ضدجوش و التیام پوست",
            'key_query': 'سرم',
            "why": "التهاب را کاهش داده و به بهبود سریع‌تر جوش‌ها کمک می‌کند.",
            "consequence": "حذف سرم باعث طولانی شدن التهاب و جوش‌ها می‌شود."
        },
        "ضدآفتاب": {
            "search_query": "ضدآفتاب بدون چربی",
            'key_query': 'ضدآفتاب',
            "why": "از پوست در برابر اشعه‌های مضر خورشید محافظت می‌کند و جای جوش را کاهش می‌دهد.",
            "consequence": "بدون ضدآفتاب، جای جوش‌ها پررنگ‌تر و ماندگارتر می‌شود."
        }
    },
    "oiliness": {
        "تونر": {
            "search_query": "تونر مات‌کننده کنترل چربی",
            'key_query': 'تونر',
            "why": "باعث کاهش چربی و مات شدن پوست می‌شود.",
            "consequence": "بدون تونر، پوست براق و چرب باقی می‌ماند."
        },
        "سرم": {
            "search_query": "سرم آبرسان سبک",
            'key_query': 'سرم',
            "why": "پوست را هیدراته می‌کند بدون اینکه چربی اضافه ایجاد کند.",
            "consequence": "حذف سرم باعث خشکی یا چربی نامتعادل پوست می‌شود."
        }
    },
    "dryness": {
        "سرم": {
            "search_query": "سرم هیالورونیک اسید آبرسان",
            'key_query': 'سرم',
            "why": "رطوبت عمقی به پوست می‌رساند و خشکی را کاهش می‌دهد.",
            "consequence": "بدون سرم، خشکی پوست ادامه یافته و حساسیت بیشتر می‌شود."
        },
        "کرم": {
            "search_query": "کرم مرطوب‌کننده قوی",
            'key_query': 'کرم',
            "why": "رطوبت را در پوست حفظ کرده و از خشک شدن جلوگیری می‌کند.",
            "consequence": "حذف کرم باعث پوسته‌پوسته شدن و خارش پوست می‌شود."
        }
    },
    "sensitivity": {
        "سرم": {
            "search_query": "سرم ترمیم‌کننده",
            'key_query': 'سرم',
            "why": "التهاب را کاهش داده و سد محافظ پوست را تقویت می‌کند.",
            "consequence": "حذف سرم باعث آسیب‌پذیری بیشتر پوست می‌شود."
        },
        "کرم": {
            "search_query": "کرم مرطوب‌کننده ضدالتهاب",
            'key_query': 'کرم',
            "why": "پوست را آرام کرده و از تحریک جلوگیری می‌کند.",
            "consequence": "بدون کرم، پوست مستعد حساسیت و قرمزی بیشتر است."
        }
    },
    "hydration": {
        "ماسک": {
            "search_query": "ماسک آبرسان شبانه",
            'key_query': 'آبرسان',
            "why": "رطوبت عمقی را تأمین کرده و پوست را نرم و لطیف می‌کند.",
            "consequence": "حذف ماسک باعث خشکی و زبری پوست می‌شود."
        },
        "کرم": {
            "search_query": "کرم مرطوب‌کننده سبک",
            'key_query': 'کرم',
            "why": "رطوبت پوست را حفظ کرده و مانع تبخیر آن می‌شود.",
            "consequence": "بدون کرم، پوست خشک و ترک‌خورده می‌شود."
        }
    },
    "elasticity": {
        "سرم": {
            "search_query": "سرم کلاژن‌ساز و لیفتینگ",
            'key_query': 'سرم',
            "why": "تولید کلاژن را تحریک کرده و خاصیت ارتجاعی پوست را بهبود می‌بخشد.",
            "consequence": "بدون سرم، افتادگی و چین‌وچروک سریع‌تر ظاهر می‌شود."
        },
        "کرم": {
            "search_query": "کرم لیفتینگ پوست",
            'key_query': 'کرم',
            "why": "پوست را سفت کرده و خطوط ریز را کاهش می‌دهد.",
            "consequence": "حذف کرم باعث شل شدن پوست و ظاهر پیرتر می‌شود."
        },
        "ضدآفتاب": {
            "search_query": "ضدآفتاب ضدپیری با SPF بالا",
            'key_query': 'ضدآفتاب',
            "why": "از آسیب نور خورشید جلوگیری کرده و پیری زودرس را کاهش می‌دهد.",
            "consequence": "بدون ضدآفتاب، روند پیری پوست سریع‌تر می‌شود."
        }
    },
    "redness": {
        "سرم": {
            "search_query": "سرم تسکین‌دهنده التهاب و قرمزی",
            'key_query': 'سرم',
            "why": "قرمزی و التهاب را کاهش می‌دهد و پوست را آرام می‌کند.",
            "consequence": "بدون سرم، قرمزی بیشتر و پوست تحریک‌پذیرتر می‌شود."
        },
        "کرم": {
            "search_query": "کرم مرطوب‌کننده ضدالتهاب",
            'key_query': 'کرم',
            "why": "سد محافظ پوست را تقویت کرده و التهاب را کاهش می‌دهد.",
            "consequence": "حذف کرم باعث افزایش حساسیت و آسیب پوست می‌شود."
        }
    }
}

PRODUCT_QUERIES_FA = {
    "cleanser": "پاک کننده صورت ملایم",
    "toner": "تونر صورت آبرسان",
    "serum": "سرم صورت ترمیم کننده",
    "moisturizer": "کرم مرطوب کننده پوست",
    "sunscreen": "ضدآفتاب صورت SPF",
    "eye_cream": "کرم دور چشم ضدتیرگی",
    "mask": "ماسک صورت روشن کننده",
    "exfoliator": "اسکراب یا لایه بردار پوست",
    "treatment": "کرم درمانی پوست",
    "oil": "روغن صورت گیاهی",
    "mist": "میست آبرسان صورت",
    "lip_care": "بالم لب ترمیم کننده",
    "ampoule": "آمپول صورت مغذی",
    "essence": "اسنس آبرسان پوست",
    "makeup_remover": "پاک کننده آرایش صورت",
    "spot_patch": "پچ ضدجوش"
}


@login_required
def routine_generator(request):
    # skin_scores = request.user.skinprofile.get_skin_scores()
    # skin_scores.sort(key=lambda x: x[1], reverse=True)
    # steps = []
    # print(skin_scores)
    # if skin_scores[0][0] == 'oiliness':
    #     steps.append({'order': 1, 'step_name': 'کاهش چربی', 'search_query': SEARCH_QUERIES['oiliness']})
    # if skin_scores[1][0] == 'sensitivity':
    #     steps.append({'order': 2, 'step_name': 'کاهش حساسیت', 'search_query': SEARCH_QUERIES['sensitivity']})

    # if not RoutinePlan.objects.filter(user=request.user).exists():
    #     RoutinePlan.objects.create(user=request.user, steps=steps)
    # else:
    #     RoutinePlan.objects.filter(user=request.user).delete()
    #     RoutinePlan.objects.create(user=request.user, steps=steps)
    # user = request.user
    # if 'oily' in user.skinprofile.skin_type:
    #     print('here')

    # full
    steps = generate_full_plan(request)
    routine, created = RoutinePlan.objects.get_or_create(
        user=request.user,
        plan_name='full',
        defaults={
            'user': request.user,
            'steps': steps,
            'plan_name': 'full'
        }
    )

    if not created:
        routine.steps = steps
        routine.save()

    # hydration
    steps = generate_hydration_plan(request)
    routine, created = RoutinePlan.objects.get_or_create(
        user=request.user,
        plan_name='hydration',
        defaults={
            'user': request.user,
            'steps': steps,
            'plan_name': 'hydration'
        }
    )

    if not created:
        routine.steps = steps
        routine.save()

    # mini
    steps = generate_mini_plan(request)
    routine, created = RoutinePlan.objects.get_or_create(
        user=request.user,
        plan_name='mini',
        defaults={
            'user': request.user,
            'steps': steps,
            'plan_name': 'mini'
        }
    )

    if not created:
        routine.steps = steps
        routine.save()

    return redirect('profile')

@login_required
def generate_full_plan(request):
    routine = []

    routine.append({
        'order': 1,
        'step_name': 'پاک‌سازی',
        'steps': [{
            "step_name": "پاک‌‌کننده",
            "search_query": "پاکسازی تمیز",
            # 'key_query': 'پاک',
            'description': STEP_DESCRIPTIONS["cleanser"]
        }]
    })

    skin_scores = request.user.skinprofile.get_skin_scores()
    skin_scores.sort(key=lambda x: abs(x[1]), reverse=True)
    for order, skin_score in enumerate(skin_scores[:3]):
        sub_steps = {}
        sub_steps['order'] = order + 2
        sub_steps['step_name'] = STEP_NAMES[skin_score[0]]
        sub_steps["steps"] = []
        for sub_step_name, sub_step_info in PROBLEM_TO_STEPS[skin_score[0]].items():
            sub_step = {}
            sub_step['step_name'] = sub_step_name
            sub_step['search_query'] = sub_step_info['search_query']
            # sub_step['key_query'] = sub_step_info['key_query']
            sub_step['description'] = ' '.join([sub_step_info['why'], sub_step_info['consequence']])
            sub_steps["steps"].append(sub_step)
        routine.append(sub_steps)

    return routine

def generate_hydration_plan(request):
    routine = []
    routine.append({
        'order': 1,
        'step_name': 'پاک‌سازی',
        'steps': [{
            "step_name": "پاک‌‌کننده",
            "search_query": "پاکسازی تمیز",
            # 'key_query': 'پاک',
            'description': STEP_DESCRIPTIONS["cleanser"]
        }]
    })

    return routine

def generate_mini_plan(request):
    routine = []
    routine.append({
        'order': 1,
        'step_name': 'پاک‌سازی',
        'steps': [{
            "step_name": "پاک‌‌کننده",
            "search_query": "پاکسازی تمیز",
            # 'key_query': 'پاک',
            'description': STEP_DESCRIPTIONS["cleanser"]
        }]
    })

    return routine



import time
from django.core.cache import cache

def find_step_products(request, name):
    start = time.time()
    routine_plan = get_object_or_404(RoutinePlan, user=request.user, plan_name=name)
    results = []
    for step in routine_plan.steps:
        subs = []
        for substep in step['steps']:
            # sub_step_products = search(request, search_query=substep['search_query'], routine=True)
            sub_step_products = routine_search(request, search_query=substep['search_query'])
            subs.append([substep['step_name'], sub_step_products, substep['description'], substep['search_query']])
        results.append([step['step_name'], subs, step['order']])

    print(time.time() - start)
    return results

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

def is_subset(list1, list2):
    return all(item in list2 for item in list1)

def both_subset(list1, list2):
    return set(list1).issubset(set(list2)) or set(list2).issubset(set(list1))

import re
from django.db.models import Case, When
import hashlib
from django.db.models import Avg, Q

@login_required
def routine_search(request, search_query):
    full_query = search_query
    full_query = re.sub(r'\s+', ' ', full_query).strip()
    full_query = re.sub(r'[^a-zA-Zآ-ی0-9۰-۹\s]', '', full_query)
    user = request.user
    raw_key = f'{user.id}:{full_query}'
    cache_key = 'routine_search' + hashlib.md5(raw_key.encode()).hexdigest()

    cached_ids = cache.get(cache_key)
    if cached_ids:
        preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(cached_ids)])
        return Product.objects.filter(id__in=cached_ids).order_by(preserved)

    query_words = full_query.lower().split()
    q_objects = Q()
    for word in query_words:
        q_objects |= Q(name__icontains=word)# | Q(brand__icontains=word) | Q(description__icontains=word)


    products = Product.objects.filter(q_objects).distinct()
    total_rating_average = Product.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    NAME_BASE_SCORE = 12000
    BRAND_BASE_SCORE = 10000
    INGREDIENT_BASE_SCORE = 8000
    CONCERN_BASE_SCORE = 10000
    SKIN_TYPE_BASE_SCORE = 10000
    RATING_BASE_SCORE = 5000
    SIMILAR_PURCHASE_BASE_SCORE = 1000000
    results = []
    base_score = 5

    # user_in = False
    # if user.is_authenticated and hasattr(user, 'skinprofile'):
    #     similar_users = get_similar_users(user.skinprofile.skin_type)
    #     user_in = True
    # else:
    #     similar_users = []


    for product in products:
        score = 0
        product_name = product.name.lower().replace('\u200c', ' ')
        product_brand = product.brand.lower().replace('\u200c', ' ')

        base_score = 50
        for word in query_words:
            name_similar = False
            brand_similar = False
            type_similar = False
            concern_similar = False

            if product_name in full_query or word in product_name.split() or word in product_name.replace(' ', '') or product_name in word.replace(' ', ''):
                name_similar = True
                score += NAME_BASE_SCORE
            
            if product_brand in full_query or word in product_brand.split():
                brand_similar = True
                score += BRAND_BASE_SCORE

            # for skin_type in product.skin_types:
            #     if both_subset(skin_type.split(), full_query.split()):
            #         type_similar = True
            #         score += SKIN_TYPE_BASE_SCORE
            #         break
            # if user_in:
            # if user.skinprofile.quiz_completed and not type_similar:
            for s_t in user.skinprofile.skin_type:
                if s_t in product.skin_types:
                    type_similar = True
                    score += SKIN_TYPE_BASE_SCORE
                    break

            # for concern_targeted in product.concerns_targeted:
            #     if both_subset(concern_targeted.split(), full_query.split()):
            #         concern_similar = True
            #         score += CONCERN_BASE_SCORE
            #         break
            # if user_in:
                if user.skinprofile.quiz_completed and not concern_similar:
                    skin_scores = SkinProfile.get_skin_scores_for_search(user.skinprofile)
                    for skin_score in skin_scores:
                        if skin_score[1] > 10:
                            for concern_targeted in product.concerns_targeted:
                                if both_subset(skin_score[0].split() in concern_targeted.split()):
                                    concern_similar = True
                                    score += CONCERN_BASE_SCORE
                                    break
                            if concern_similar:
                                break

            # if not any([name_similar, brand_similar, concern_similar, type_similar, ingredient_similar]):
            #     base_score = 5
            #     name_similarity = 0
            #     name_counter = 0
            #     for p_word in product_name.split():
            #         s = similarity(word, p_word)
            #         if s > 90:
            #             name_similarity = NAME_BASE_SCORE
            #             name_counter = 1
            #             break
            #         name_similarity += NAME_BASE_SCORE ** similarity(word, p_word)
            #         name_counter += 1
            #     name_similarity /= name_counter
            #     name_similar = True if name_similarity > 0.85 * NAME_BASE_SCORE else False
            #     # score += name_similarity
            #     brand_similarity = BRAND_BASE_SCORE ** similarity(word, product_brand)
            #     brand_similar = True if brand_similarity > 0.85 * BRAND_BASE_SCORE else False
            #     # score += brand_similarity

            #     if not concern_similar and not name_similar and not brand_similar:
            #         concern_counter = 0
            #         concern_similarity = 0
            #         found = False
            #         for concern in product.concerns_targeted:
            #             if word in concern.split():
            #                 concern_similarity = CONCERN_BASE_SCORE
            #                 concern_counter = 1
            #                 break
            #             for p_concern in concern.split():
            #                 c = similarity(word, p_concern)
            #                 if c > 0.9:
            #                     concern_similarity = CONCERN_BASE_SCORE
            #                     concern_counter = 1
            #                     found = True
            #                     break
            #                 concern_similarity += CONCERN_BASE_SCORE ** c
            #                 concern_counter += 1
            #             if found:
            #                 break
            #         concern_similarity /= concern_counter
            #         concern_similar = True if concern_similarity > 0.85 * CONCERN_BASE_SCORE else False
            #         # score += concern_similarity
            #         # score += max(name_similarity, brand_similarity, ingredient_similarity, concern_similarity)
            #     else:
            #         concern_similar = False
            #         concern_similarity = 0
                    
            #     if not concern_similar and not ingredient_similar and not name_similar and not brand_similar:
            #         type_counter = 0
            #         type_similarity = 0
            #         if word in product.get_skin_types_fa():
            #             type_similarity = SKIN_TYPE_BASE_SCORE
            #             type_counter = 1
            #         else:
            #             for skin_type in product.get_skin_types_fa():
            #                 st = similarity(word, skin_type)
            #                 if st > 0.9:
            #                     type_similarity = SKIN_TYPE_BASE_SCORE
            #                     type_counter = 1
            #                     break
            #                 type_similarity += SKIN_TYPE_BASE_SCORE ** st
            #                 type_counter += 1
            #         if type_counter == 0:
            #             type_counter = 1
            #         type_similarity /= type_counter
            #         type_similar = True if type_similarity > 0.85 * SKIN_TYPE_BASE_SCORE else False       
            #     else:
            #         type_similar = False
            #         type_similarity = 0

            #     if not name_similar and not brand_similar and not type_similar and not concern_similar:
            #         ingredient_counter = 0
            #         ingredient_similarity = 0
            #         found = False
            #         for ingredient in product.ingredients:
            #             if word in ingredient.split():
            #                 ingredient_similarity = INGREDIENT_BASE_SCORE
            #                 ingredient_counter = 1
            #                 break
            #             for p_ingredient in ingredient.split():
            #                 i = similarity(word, p_ingredient)
            #                 if i > 0.9:
            #                     ingredient_similarity = INGREDIENT_BASE_SCORE
            #                     ingredient_counter = 1
            #                     found = True
            #                     break
            #                 ingredient_similarity += INGREDIENT_BASE_SCORE ** i
            #                 ingredient_counter += 1
            #             if found:
            #                 break
            #         ingredient_similarity /= ingredient_counter
            #         # score += ingredient_similarity
            #         ingredient_similar = True if ingredient_similarity > 0.85 * INGREDIENT_BASE_SCORE else False
            #     else:
            #         ingredient_similar = False
            #         ingredient_similarity = 0

            #     if type_similar:
            #         score += type_similarity
            #     else:
            #         n = name_similarity / NAME_BASE_SCORE
            #         b = brand_similarity / BRAND_BASE_SCORE
            #         i = ingredient_similarity / INGREDIENT_BASE_SCORE
            #         c = concern_similarity / CONCERN_BASE_SCORE
            #         t = type_similarity / SKIN_TYPE_BASE_SCORE
            #         if n > max(b, i, c, t):
            #             score += name_similarity
            #         elif b > max(i, c, t):
            #             score += brand_similarity
            #         elif i > max(c, t):
            #             score += ingredient_similarity
            #         elif c > t:
            #             score += concern_similarity
            #         else:
            #             score += type_similarity



        if score > base_score + 1:
            results.append((product.id, score + RATING_BASE_SCORE ** bayesian_average(product, total_rating_average)))
            
    results.sort(key=lambda x: x[1], reverse=True)
    selected_ids = [r[0] for r in results[:5]]
    cache.set(cache_key, selected_ids, timeout=86400)
    preserved = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(selected_ids)])
    return Product.objects.filter(id__in=selected_ids).order_by(preserved)