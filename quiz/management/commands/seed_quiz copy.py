from django.core.management.base import BaseCommand
from quiz.models import Question, Choice

class Command(BaseCommand):
    help = "Seed the database with 20 quiz questions and choices for skin analysis"

    quiz_data = [

        {
            # Main question 1 about SkinType
            "order": 1,
            "type": "single",
            "text": "نوع پوست خود را چگونه ارزیابی می‌کنید؟ (در صورت پاسخ به این سؤال، نیازی به پاسخ به سوالات ۲ تا ۷ نیست)",
            "choices": [
                ("پوست خشک", {"skin_type": "dry"}),
                ("پوست چرب", {"skin_type": "oily"}),
                ("پوست نرمال", {"skin_type": "normal"}),
                ("پوست مختلط (ترکیبی)", {"skin_type": "combination"}),
                ("پوست حساس", {"skin_type": "sensitive"}),
                ("نمی‌دانم", {}), # -> Active next 5 questions
            ],
        },


        {
            # Sub Question 1.1
            "order": 2,
            "type": "scale",
            "text": "در طول روز پوست شما چقدر چرب می‌شود؟ از ۱ (اصلاً) تا ۵ (خیلی زیاد)",
            "scale_effect_map": {
                "1": {"dryness": 2},
                "2": {"dryness": 1},
                "3": {},
                "4": {"oiliness": 1},
                "5": {"oiliness": 2},
            },
        },

        {
            # Sub question 1.2
            "order": 3,
            "type": "scale",
            "text": "پوستتان چقدر کشیده یا پوسته‌پوسته می‌شود؟ از ۱ (هیچ‌وقت) تا ۵ (همیشه)",
            "scale_effect_map": {
                "1": {},
                "2": {"dryness": 1},
                "3": {"dryness": 2},
                "4": {"dryness": 3},
                "5": {"dryness": 4},
            },
        },
        
        {
            # Sub question 1.3
            "order": 4,
            "type": "multiple",
            "text": "در کدام نواحی از صورت خود چربی یا خشکی احساس می‌کنید؟",
            "choices": [
                ("پیشانی چرب، گونه‌ها خشک", {"skin_type": "combination"}),
                ("کل صورت چرب", {"oiliness": 2}),
                ("کل صورت خشک", {"dryness": 2}),
                ("نواحی مختلف وضعیت متفاوتی دارند", {"skin_type": "combination"}),
                ("تفاوتی احساس نمی‌کنم", {}),
            ],
        },

        {
            #Sub question 1.4
            "order": 5,
            "type": "single",
            "text": "واکنش پوست شما به تغییر فصل چیست؟",
            "choices": [
                ("در زمستان خشک و پوسته‌پوسته می‌شود", {"dryness": 2}),
                ("در تابستان چرب و براق می‌شود", {"oiliness": 2}),
                ("در هر فصل نیاز به مراقبت متفاوت دارد", {"skin_type": "combination"}),
                ("تغییر خاصی نمی‌کند", {"skin_type": "normal"}),
            ],
        },
        
        
        {
            # Sub question 1.5
            "order": 6,
            "type": "multiple",
            "text": "پس از استفاده از محصولات پوستی، چه واکنشی از پوستتان می‌بینید؟",
            "choices": [
                ("سوزش یا خارش", {"skin_type": "sensitive", "sensitivity": 1}),
                ("چرب‌تر شدن پوست", {"oiliness": 1}),
                ("خشک‌تر شدن پوست", {"dryness": 1}),
                ("هیچ واکنشی", {}),
            ],
        },


        {
            "order": 7,
            "type": "single",
            "text": "پس از شستشوی صورت، پوستتان چه حسی دارد؟",
            "choices": [
                ("خیلی خشک می‌شود و کشیده می‌شود", {"dryness": 2}),
                ("بلافاصله چرب می‌شود", {"oiliness": 2}),
                ("نیاز فوری به مرطوب‌کننده دارد", {"dryness": 1}),
                ("حس نرمال و متعادل دارد", {"skin_type": "normal"}),
            ],
        },
        
# --------------------------------------------------------------------------------------------#
# -------------------------- ACNE --------------------------#
        {
            "order": 8,
            "type": "range",
            "text": "پوست شما تا چه حد مستعد جوش زدن است؟ (۰ به معنی بدون جوش و ۱۰ بسیار مستعد) در صورتی که به این سؤال پاسخ می‌دهید، نیازی به پاسخ دادن به ۵ سؤال بعدی نیست.",
            # "range_min": 0,
            # "range_max": 10,
            "effects": {
                "acne": "value"
            },
        },


        {
            "order": 9,
            "type": "single",
            "text": "چند وقت یک‌بار دچار جوش یا آکنه می‌شوید؟",
            "choices": [
                ("تقریباً هر روز", {"acne": 9}),
                ("چند بار در هفته", {"acne": 7}),
                ("فقط گاهی، مثلاً قبل از عادت ماهانه یا استرس", {"acne": 4}),
                ("به ندرت یا هرگز", {"acne": 1})
            ]
        },
        
        
        {
            "order": 10,
            "type": "single",
            "text": "کدام توصیف به پوست شما نزدیک‌تر است؟",
            "choices": [
                ("معمولاً منافذ پوستم باز و قابل مشاهده‌اند", {"acne": 7}),
                ("گاهی منافذم قابل مشاهده‌اند", {"acne": 4}),
                ("منافذم کوچک و کمتر قابل دیدن‌اند", {"acne": 2}),
                ("منافذم خیلی کوچک یا نامشخص‌اند", {"acne": 0})
            ]
        },


        {
            "order": 11,
            "type": "single",
            "text": "آیا سابقه استفاده از محصولات ضدجوش یا داروهای پوستی دارید؟",
            "choices": [
                ("بله، همچنان استفاده می‌کنم", {"acne": 8}),
                ("قبلاً استفاده می‌کردم ولی حالا نه", {"acne": 5}),
                ("خیلی کم یا فقط برای مواقع خاص", {"acne": 2}),
                ("نه، هیچ‌وقت", {"acne": 0})
            ]
        },
        
        
        {
            "order": 12,
            "type": "single",
            "text": "چه زمانی بیشترین احتمال جوش زدن دارید؟",
            "choices": [
                ("تقریباً در تمام شرایط", {"acne": 8}),
                ("مواقع استرس یا قاعدگی", {"acne": 5}),
                ("در گرما یا تعریق زیاد", {"acne": 4}),
                ("خیلی به ندرت اتفاق می‌افتد", {"acne": 1})
            ]
        },


        {
            "order": 13,
            "type": "single",
            "text": "پوست شما بعد از یک روز بیرون بودن در گرما چه حالتی پیدا می‌کند؟",
            "choices": [
                ("چرب و همراه با جوش‌های جدید", {"acne": 7}),
                ("کمی چرب ولی بدون جوش", {"acne": 4}),
                ("تغییر خاصی نمی‌کند", {"acne": 2}),
                ("خشک‌تر از حالت عادی می‌شود", {"acne": 0})
            ]
        },
        
# -------------------------- Sensivity Questions --------------------------#

        {
            "order": 14,
            "type": "range",
            "text": "پوست شما چقدر حساس است؟ (۰ = اصلاً حساس نیست، ۱۰ = خیلی حساس)\n(در صورت پاسخ به این سوال، نیازی به پاسخ‌دادن به ۵ سوال بعدی نیست)",
            "min": 0,
            "max": 10,
            "effect_field": "sensitivity"
        },


        {
            "order": 15,
            "type": "single",
            "text": "بعد از استفاده از یک محصول جدید مراقبت پوستی، پوست شما چگونه واکنش نشان می‌دهد؟",
            "choices": [
                ("خیلی سریع قرمز یا تحریک می‌شود", {"sensitivity": 2}),
                ("کمی احساس سوزش یا قرمزی دارم", {"sensitivity": 1}),
                ("تغییری حس نمی‌کنم", {"sensitivity": 0})
            ]
        },
        
        
        {
            "order": 16,
            "type": "single",
            "text": "در مواجهه با آب داغ یا سرد، پوست صورت شما چگونه واکنش می‌دهد؟",
            "choices": [
                ("قرمز می‌شود یا می‌سوزد", {"sensitivity": 2}),
                ("کمی اذیت می‌شود", {"sensitivity": 1}),
                ("هیچ مشکلی ندارد", {"sensitivity": 0})
            ]
        },


        {
            "order": 17,
            "type": "single",
            "text": "در برابر نور خورشید بدون ضدآفتاب چه واکنشی دارید؟",
            "choices": [
                ("خیلی سریع قرمز می‌شوم", {"sensitivity": 2}),
                ("کمی آفتاب‌سوخته می‌شوم", {"sensitivity": 1}),
                ("مشکلی ندارم", {"sensitivity": 0})
            ]
        },
        
        
        {
            "order": 18,
            "type": "single",
            "text": "بعد از اصلاح صورت (مثلاً با تیغ یا موم)، پوستتان چه حالتی دارد؟",
            "choices": [
                ("خیلی قرمز و ملتهب می‌شود", {"sensitivity": 2}),
                ("تا حدی قرمز می‌شود", {"sensitivity": 1}),
                ("تغییری نمی‌کند", {"sensitivity": 0})
            ]
        },

        {
            "order": 19,
            "type": "single",
            "text": "آیا تا به حال در اثر استفاده از یک کرم یا شوینده دچار خارش، سوزش یا التهاب شده‌اید؟",
            "choices": [
                ("بله، چندین بار", {"sensitivity": 2}),
                ("گاهی اوقات", {"sensitivity": 1}),
                ("خیر، هیچ‌وقت", {"sensitivity": 0})
            ]
        },

# -------------------------- Dryness Questions --------------------------#

        # Main Question
        {
            "order": 20,
            "type": "range",
            "text": "پوست شما تا چه حد احساس خشکی دارد؟ (۰ = اصلاً خشک نیست، ۱۰ = بسیار خشک)\n(در صورت پاسخ به این سؤال، نیازی به پاسخ‌دادن به ۵ سؤال بعدی نیست)",
            "min": 0,
            "max": 10,
            "effects": {"dryness": "value"}
        },
        
        # Sub Questions
        {
            "order": 21,
            "type": "single",
            "text": "آیا پس از شستن صورتتان احساس کشیدگی یا سفتی در پوست دارید؟",
            "choices": [
              ("بله، اغلب اوقات", {"dryness": 3}),
              ("گاهی اوقات", {"dryness": 1}),
              ("نه، هرگز", {"dryness": 0})
            ]
        },
        
        {
            "order": 22,
            "type": "single",
            "text": "آیا در پوست صورتتان پوسته‌پوسته شدن را تجربه می‌کنید؟",
            "choices": [
              ("بله، به‌طور مرتب", {"dryness": 3}),
              ("فقط در زمستان یا هوای سرد", {"dryness": 2}),
              ("خیلی کم یا اصلاً نه", {"dryness": 0})
            ]
        },

        {
            "order": 23,
            "type": "single",
            "text": "پس از استفاده از شوینده، آیا نیاز فوری به کرم مرطوب‌کننده دارید؟",
            "choices": [
              ("بله، حتماً باید استفاده کنم", {"dryness": 3}),
              ("گاهی اوقات", {"dryness": 1}),
              ("نه، نیازی نیست", {"dryness": 0})
            ]
        },
        
        {
            "order": 24,
            "type": "single",
            "text": "سطح پوست صورت شما بیشتر چگونه به نظر می‌رسد؟",
            "choices": [
              ("کدر و پوسته‌پوسته", {"dryness": 3}),
              ("طبیعی و صاف", {"dryness": 1}),
              ("براق یا چرب", {"dryness": 0})
            ]
        },
        
        {
            "order": 25,
            "type": "single",
            "text": "در نواحی مثل گونه‌ها یا اطراف دهان، بیشتر چه احساسی دارید؟",
            "choices": [
              ("خشکی و ترک‌خوردگی", {"dryness": 3}),
              ("کمی خشکی گاه‌به‌گاه", {"dryness": 1}),
              ("احساس نرمی یا چربی", {"dryness": 0})
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

        self.stdout.write(self.style.SUCCESS("All 20 questions added successfully."))
