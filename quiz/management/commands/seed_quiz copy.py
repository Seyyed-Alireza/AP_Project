from django.core.management.base import BaseCommand
from quiz.models import Question, Choice

class Command(BaseCommand):
    help = "Seed the database with 20 quiz questions and choices for skin analysis"

    quiz_data = [
        
# -------------------------- ACNE --------------------------#
        {
            "order": 1,
            "type": "range",
            "text": "پوست شما تا چه حد مستعد جوش زدن است؟ (۰ به معنی بدون جوش و ۱۰ بسیار مستعد)\nدر صورتی که به این سؤال پاسخ می‌دهید، نیازی به پاسخ دادن به ۵ سؤال بعدی نیست.",
            "range_effect_map": {str(i): {"acne": i} for i in range(0, 11)}
        },

        {
            "order": 2,
            "type": "single",
            "text": "چند وقت یک‌بار دچار جوش یا آکنه می‌شوید؟",
            "choices": [
                ("تقریباً هر روز", {"acne": 3, "oiliness": 1}),
                ("چند بار در هفته", {"acne": 2}),
                ("فقط گاهی، مثلاً قبل از استرس", {"acne": 1, "sensitivity": 1}),
                ("به ندرت یا هرگز", {"acne": 0})
            ]
        },

        {
            "order": 3,
            "type": "single",
            "text": "کدام توصیف به پوست شما نزدیک‌تر است؟",
            "choices": [
                ("معمولاً منافذ پوستم باز و قابل مشاهده‌اند", {"acne": 2, "oiliness": 2}),
                ("گاهی منافذم قابل مشاهده‌اند", {"acne": 1, "oiliness": 1}),
                ("منافذم کوچک و کمتر قابل دیدن‌اند", {"acne": 0}),
                ("منافذم خیلی کوچک یا نامشخص‌اند", {"acne": -1, "oiliness": -1})
            ]
        },

        {
            "order": 4,
            "type": "single",
            "text": "آیا سابقه استفاده از محصولات ضدجوش یا داروهای پوستی دارید؟",
            "choices": [
                ("بله، همچنان استفاده می‌کنم", {"acne": 3}),
                ("قبلاً استفاده می‌کردم ولی حالا نه", {"acne": 1}),
                ("خیلی کم یا فقط برای مواقع خاص", {"acne": 0}),
                ("نه، هیچ‌وقت", {"acne": -1})
            ]
        },

        {
            "order": 5,
            "type": "single",
            "text": "چه زمانی بیشترین احتمال جوش زدن دارید؟",
            "choices": [
                ("تقریباً در تمام شرایط", {"acne": 3}),
                ("مواقع استرس", {"acne": 2, "sensitivity": 1}),
                ("در گرما یا تعریق زیاد", {"acne": 2, "oiliness": 1}),
                ("خیلی به ندرت اتفاق می‌افتد", {"acne": 0})
            ]
        },

        {
            "order": 6,
            "type": "single",
            "text": "پوست شما بعد از یک روز بیرون بودن در گرما چه حالتی پیدا می‌کند؟",
            "choices": [
                ("چرب و همراه با جوش‌های جدید", {"acne": 3, "oiliness": 2}),
                ("کمی چرب ولی بدون جوش", {"oiliness": 1}),
                ("تغییر خاصی نمی‌کند", {}),
                ("خشک‌تر از حالت عادی می‌شود", {"acne": -1, "dryness": 1})
            ]
        },
        
# -------------------------- Sensivity Questions --------------------------#

        {
            "order": 7,
            "type": "range",
            "text": "پوست شما چقدر حساس است؟ (۰ = اصلاً حساس نیست، ۱۰ = خیلی حساس)\n(در صورت پاسخ به این سوال، نیازی به پاسخ‌دادن به ۵ سوال بعدی نیست)",
            "range_effect_map": {str(i): {"sensitivity": i} for i in range(0, 11)}
        },

        {
            "order": 8,
            "type": "single",
            "text": "بعد از استفاده از یک محصول جدید مراقبت پوستی، پوست شما چگونه واکنش نشان می‌دهد؟",
            "choices": [
                ("خیلی سریع قرمز یا تحریک می‌شود", {"sensitivity": 2}),
                ("کمی احساس سوزش یا قرمزی دارم", {"sensitivity": 1}),
                ("تغییری حس نمی‌کنم", {"sensitivity": -1})
            ]
        },

        {
            "order": 9,
            "type": "single",
            "text": "در مواجهه با آب داغ یا سرد، پوست صورت شما چگونه واکنش می‌دهد؟",
            "choices": [
                ("قرمز می‌شود یا می‌سوزد", {"sensitivity": 2}),
                ("کمی اذیت می‌شود", {"sensitivity": 0}),
                ("هیچ مشکلی ندارد", {"sensitivity": -1})
            ]
        },

        {
            "order": 10,
            "type": "single",
            "text": "در برابر نور خورشید بدون ضدآفتاب چه واکنشی دارید؟",
            "choices": [
                ("خیلی سریع قرمز می‌شوم", {"sensitivity": 3}),
                ("کمی آفتاب‌سوخته می‌شوم", {"sensitivity": 1}),
                ("مشکلی ندارم", {"sensitivity": -2})
            ]
        },

        {
            "order": 11,
            "type": "single",
            "text": "بعد از اصلاح صورت (مثلاً با تیغ یا موم)، پوستتان چه حالتی دارد؟",
            "choices": [
                ("خیلی قرمز و ملتهب می‌شود", {"sensitivity": 2}),
                ("تا حدی قرمز می‌شود", {"sensitivity": 0}),
                ("تغییری نمی‌کند", {"sensitivity": -1})
            ]
        },

        {
            "order": 12,
            "type": "single",
            "text": "آیا تا به حال در اثر استفاده از یک کرم یا شوینده دچار خارش، سوزش یا التهاب شده‌اید؟",
            "choices": [
                ("بله، چندین بار", {"sensitivity": 3}),
                ("گاهی اوقات", {"sensitivity": 1}),
                ("خیر، هیچ‌وقت", {"sensitivity": -1})
            ]
        },

# -------------------------- Dryness Questions --------------------------#

        # Main Question
        {
            "order": 13,
            "type": "range",
            "text": "پوست شما تا چه حد احساس خشکی دارد؟ (۰ = اصلاً خشک نیست، ۱۰ = بسیار خشک)\n(در صورت پاسخ به این سؤال، نیازی به پاسخ‌دادن به ۵ سؤال بعدی نیست)",
            "range_effect_map": {str(i): {"dryness": i} for i in range(0, 11)}
        },

        # Sub Question
        {
            "order": 14,
            "type": "single",
            "text": "آیا پس از شستن صورتتان احساس کشیدگی یا سفتی در پوست دارید؟",
            "choices": [
                ("بله، اغلب اوقات", {"dryness": 3}),
                ("گاهی اوقات", {"dryness": 1}),
                ("نه، هرگز", {"dryness": -1})
            ]
        },

        {
            "order": 15,
            "type": "single",
            "text": "آیا در پوست صورتتان پوسته‌پوسته شدن را تجربه می‌کنید؟",
            "choices": [
                ("بله، به‌طور مرتب", {"dryness": 3}),
                ("فقط در زمستان یا هوای سرد", {"dryness": 1}),
                ("خیلی کم یا اصلاً نه", {"dryness": -1})
            ]
        },

        {
            "order": 16,
            "type": "single",
            "text": "پس از استفاده از شوینده، آیا نیاز فوری به کرم مرطوب‌کننده دارید؟",
            "choices": [
                ("بله، حتماً باید استفاده کنم", {"dryness": 3}),
                ("گاهی اوقات", {"dryness": 1}),
                ("نه، نیازی نیست", {"dryness": -1})
            ]
        },

        {
            "order": 17,
            "type": "single",
            "text": "سطح پوست صورت شما بیشتر چگونه به نظر می‌رسد؟",
            "choices": [
                ("کدر و پوسته‌پوسته", {"dryness": 3}),
                ("طبیعی و صاف", {"dryness": 1}),
                ("براق یا چرب", {"dryness": -2})
            ]
        },

        {
            "order": 18,
            "type": "single",
            "text": "در نواحی مثل گونه‌ها یا اطراف دهان، بیشتر چه احساسی دارید؟",
            "choices": [
                ("خشکی و ترک‌خوردگی", {"dryness": 3}),
                ("کمی خشکی گاه‌به‌گاه", {"dryness": 1}),
                ("احساس نرمی یا چربی", {"dryness": -1})
            ]
        }

# -------------------------- Oilness Questions --------------------------#

        # Main question
        {
            "order": 19,
            "type": "range",
            "text": "پوست شما تا چه حد چرب است؟ (۰ = اصلاً چرب نیست، ۱۰ = بسیار چرب)\n(در صورت پاسخ به این سؤال، نیازی به پاسخ‌دادن به ۵ سؤال بعدی نیست)",
            "range_effect_map": {str(i): {"oiliness": i} for i in range(0, 11)}
        },

        {
            "order": 20,
            "type": "single",
            "text": "آیا پوست صورتتان در طول روز برق می‌زند یا چرب می‌شود؟",
            "choices": [
                ("بله، در بیشتر مواقع", {"oiliness": 3}),
                ("فقط در ناحیه T یا در هوای گرم", {"oiliness": 2}),
                ("به‌ندرت یا اصلاً نه", {"oiliness": -1})
            ]
        },

        {
            "order": 21,
            "type": "single",
            "text": "آیا هنگام لمس صورت خود احساس چربی یا لغزندگی می‌کنید؟",
            "choices": [
                ("بله، به‌طور دائم", {"oiliness": 3}),
                ("فقط در آخر روز", {"oiliness": 1}),
                ("خیر، همیشه خشک یا نرمال است", {"oiliness": -1})
            ]
        },

        {
            "order": 22,
            "type": "single",
            "text": "پس از شستن صورت، چه مدت طول می‌کشد تا دوباره چرب شود؟",
            "choices": [
                ("کمتر از ۱ ساعت", {"oiliness": 3}),
                ("۲ تا ۳ ساعت", {"oiliness": 2}),
                ("خیلی دیر یا اصلاً چرب نمی‌شود", {"oiliness": -1})
            ]
        },

        {
            "order": 23,
            "type": "single",
            "text": "آیا جوش‌های سرسیاه یا منافذ باز زیادی دارید؟",
            "choices": [
                ("بله، روی بینی، پیشانی یا گونه‌ها", {"oiliness": 2}),
                ("در برخی نقاط خاص", {"oiliness": 1}),
                ("خیر، اصلاً یا خیلی کم", {"oiliness": -1})
            ]
        },

        {
            "order": 24,
            "type": "single",
            "text": "هنگام استفاده از محصولات آرایشی یا مراقبتی، آیا زود چرب یا براق می‌شوند؟",
            "choices": [
                ("بله، خیلی سریع", {"oiliness": 3}),
                ("بعد از چند ساعت", {"oiliness": 1}),
                ("خیر، اصلاً این مشکل را ندارم", {"oiliness": -1})
            ]
        },
        
# -------------------------- Redness Questions --------------------------#
        
        # Main Question
        {
        "order": 25,
        "type": "range",
        "text": "پوست شما چقدر مستعد قرمزی است؟ (۰ = اصلاً قرمز نمی‌شود، ۱۰ = خیلی سریع و شدید قرمز می‌شود)\n(اگر به این سوال پاسخ دادید، نیازی به پاسخ دادن به ۵ سوال بعدی نیست)",
        "range_effect_map": {str(i): {"redness": i} for i in range(0, 11)}
    },

    {
        "order": 26,
        "type": "single",
        "text": "پس از قرار گرفتن در معرض آفتاب بدون ضدآفتاب، پوست شما چه واکنشی نشان می‌دهد؟",
        "choices": [
            ("خیلی سریع قرمز و ملتهب می‌شود", {"redness": 3}),
            ("کمی قرمز می‌شود", {"redness": 1}),
            ("تغییری نمی‌کند", {"redness": 0}),
            ("کمتر قرمز می‌شود یا هیچ واکنشی ندارد", {"redness": -1})
        ]
    },

    {
        "order": 27,
        "type": "single",
        "text": "آیا پوستتان هنگام تغییرات دمای شدید (مثل سرما یا گرما) قرمز می‌شود؟",
        "choices": [
            ("بله، خیلی سریع", {"redness": 3}),
            ("گاهی اوقات", {"redness": 1}),
            ("نه، معمولاً خیر", {"redness": 0}),
            ("معمولاً کمتر قرمز می‌شود", {"redness": -1})
        ]
    },

    {
        "order": 28,
        "type": "single",
        "text": "آیا در پوست صورتتان نقاط قرمز یا جوش‌های قرمز رنگ دیده می‌شود؟",
        "choices": [
            ("بله، به طور مکرر", {"redness": 3}),
            ("گاه به گاه", {"redness": 1}),
            ("معمولاً کمتر قرمز است", {"redness": 0})
            ("خیر، اصلاً", {"redness": -1}),
        ]
    },

    {
        "order": 29,
        "type": "single",
        "text": "آیا پوستتان به محصولات مراقبتی یا آرایشی حساسیت نشان می‌دهد و قرمز می‌شود؟",
        "choices": [
            ("بله، اغلب", {"redness": 3}),
            ("گاهی", {"redness": 1}),
            ("خیر، هرگز", {"redness": 0}),
            ("معمولاً هیچ واکنشی ندارد", {"redness": -1})
        ]
    },

    {
        "order": 30,
        "type": "single",
        "text": "آیا پوست شما به دلیل استرس یا تغییرات هورمونی قرمز و ملتهب می‌شود؟",
        "choices": [
            ("بله، زیاد", {"redness": 3}),
            ("گاهی", {"redness": 1}),
            ("نه، معمولاً خیر", {"redness": 0}),
            ("کمتر قرمز می‌شود", {"redness": -1})
        ]
    },

# -------------------------- Hydration Questions --------------------------#

        # Main question
        {
            "order": 31,
            "type": "range",
            "text": "میزان رطوبت پوست شما را چگونه ارزیابی می‌کنید؟ (۰ = بسیار خشک، ۱۰ = بسیار مرطوب)\n(اگر به این سوال پاسخ دادید، نیازی به پاسخ دادن به ۵ سوال بعدی نیست)",
            "range_effect_map": {str(i): {"hydration": i} for i in range(0, 11)}
        },

        {
            "order": 32,
            "type": "single",
            "text": "پس از شست‌وشوی صورت، چه احساسی روی پوستتان دارید؟",
            "choices": [
                ("خیلی خشک و کشیده", {"hydration": -2}),
                ("کمی خشک", {"hydration": -1}),
                ("نرمال یا مرطوب", {"hydration": 1})
            ]
        },

        {
            "order": 33,
            "type": "single",
            "text": "آیا پوستتان پوسته‌پوسته می‌شود یا ترک می‌خورد؟",
            "choices": [
                ("بله، به طور مداوم", {"hydration": -2}),
                ("فقط در زمستان یا شرایط خاص", {"hydration": -1}),
                ("خیر، اصلاً", {"hydration": 1})
            ]
        },

        {
            "order": 34,
            "type": "single",
            "text": "آیا احساس کشیدگی یا سوزش در پوستتان وجود دارد؟",
            "choices": [
                ("بله، بیشتر اوقات", {"hydration": -2}),
                ("گاه‌به‌گاه", {"hydration": -1}),
                ("نه، معمولاً خیر", {"hydration": 1})
            ]
        },

        {
            "order": 35,
            "type": "single",
            "text": "آیا از مرطوب‌کننده استفاده می‌کنید؟ اگر بله، چند بار در روز؟",
            "choices": [
                ("اصلاً استفاده نمی‌کنم", {"hydration": -1}),
                ("یک بار در روز", {"hydration": 1}),
                ("بیش از یک بار در روز", {"hydration": 2})
            ]
        },

        {
            "order": 36,
            "type": "single",
            "text": "آیا در طول روز نیاز دارید که چندین بار از مرطوب‌کننده یا آب‌پاش استفاده کنید؟",
            "choices": [
                ("بله، چندین بار", {"hydration": -2}),
                ("فقط یک بار", {"hydration": -1}),
                ("نه، نیازی نیست", {"hydration": 1})
            ]
        },

# -------------------------- Elasticity Questions --------------------------#

        # Main question
        {
            "order": 37,
            "type": "range",
            "text": "کشسانی یا انعطاف‌پذیری پوستتان را چقدر ارزیابی می‌کنید؟ (۰ = کاملاً شل و افتاده، ۱۰ = سفت و کشسان)\n(اگر به این سؤال پاسخ دهید، نیازی به پاسخ دادن به ۵ سؤال بعدی نیست)",
            "min": 0,
            "max": 10,
            "range_effect_map": {str(i): {"elasticity": i} for i in range(0, 11)},
        },

        # Sub-question
        {
            "order": 38,
            "type": "single",
            "text": "آیا پوست صورتتان افتادگی یا شلی دارد؟",
            "choices": [
                ("بله، به وضوح قابل مشاهده است", {"elasticity": -2}),
                ("کمی، در نواحی خاصی", {"elasticity": -1}),
                ("خیر، پوست سفتی دارم", {"elasticity": 1})
            ]
        },

        {
            "order": 39,
            "type": "single",
            "text": "آیا هنگام لبخند یا حرکت صورت، خطوط پوستی دیرتر به حالت عادی برمی‌گردند؟",
            "choices": [
                ("بله، کاملاً مشهود است", {"elasticity": -2}),
                ("کمی، اما زیاد محسوس نیست", {"elasticity": -1}),
                ("خیر، پوست سریع برمی‌گردد", {"elasticity": 1})
            ]
        },

        {
            "order": 40,
            "type": "single",
            "text": "آیا پوستتان قابلیت بازگشت سریع به حالت اولیه بعد از کشش را دارد؟",
            "choices": [
                ("خیر، خیلی کند بازمی‌گردد", {"elasticity": -2}),
                ("نسبتاً کند", {"elasticity": -1}),
                ("بله، سریع و قابل‌قبول", {"elasticity": 1})
            ]
        },

        {
            "order": 41,
            "type": "single",
            "text": "آیا از محصولات ضد پیری یا افزایش‌دهنده کشسانی استفاده می‌کنید؟",
            "choices": [
                ("خیر", {"elasticity": 0}),
                ("به‌ندرت", {"elasticity": 1}),
                ("مرتب استفاده می‌کنم", {"elasticity": 2})
            ]
        },

        {
            "order": 42,
            "type": "single",
            "text": "سن تقریبی شما چقدر است؟",
            "choices": [
                ("زیر ۲۵ سال", {"elasticity": 2}),
                ("۲۵ تا ۳۵ سال", {"elasticity": 1}),
                ("۳۵ تا ۵۰ سال", {"elasticity": 0}),
                ("بیشتر از ۵۰ سال", {"elasticity": -1})
            ]
        },
    ]

    
    def handle(self, *args, **options):
        self.stdout.write("Adding questions to database...")

        for q in self.quiz_data:
            qtype = q.get("type", "single")
            order = q["order"]
            question_obj, created = Question.objects.get_or_create(
                order=order,
                defaults={"text": q["text"], "type": qtype}
            )
            if not created:
                self.stdout.write(f"Question {order} exists, skipped.")
                continue

            if qtype in ["single", "multiple", "age_range"]:
                for text, effects in q["choices"]:
                    Choice.objects.create(question=question_obj, text=text, effects=effects or {})

            elif qtype == "range":
                for rng, effects in q["range_effect_map"].items():
                    Choice.objects.create(question=question_obj, text=rng, effects=effects or {})

            elif qtype == "scale":
                for val, effects in q["scale_effect_map"].items():
                    Choice.objects.create(question=question_obj, text=f"{val}", effects=effects or {})

            elif qtype == "boolean":
                for label, effects in q["boolean_effects"].items():
                    text = "بله" if label == "yes" else "خیر"
                    Choice.objects.create(question=question_obj, text=text, effects=effects or {})

            self.stdout.write(self.style.SUCCESS(f"Question {order} added."))

        self.stdout.write(self.style.SUCCESS("All questions added successfully."))
