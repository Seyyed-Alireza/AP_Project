from django.core.management.base import BaseCommand
from quiz.models import Question, Choice

class Command(BaseCommand):
    help = "Seed the database with 20 quiz questions and choices for skin analysis"

    quiz_data = [
        # Single-choice (radio) - at least 2
        {
            "order": 1,
            "type": "single",
            "text": "نوع پوست خود را چگونه ارزیابی می‌کنید؟ (اگر به این سؤال جواب دادید سؤالات دو تا هغت را رد کنید)",
            "choices": [
                ('پوست خشک', {'skin_type': 'dry'}),
                ('پوست چرب', {'skin_type': 'oily'}),
                ('پوست نرمال', {'skin_type': 'normal'}),
                ('پوست مختلط (ترکیبی)', {'skin_type': 'combination'}),
                ('پوست حساس', {'skin_type': 'sensitive'}),
            ],
        },
        {
            "order": 2,
            "type": "single",
            "text": "پوست شما چند وقت یک بار دچار جوش می‌شود؟",
            "choices": [
                ("هر هفته چند بار", {"acne": True}),
                ("هر ماه یکبار", {"acne": True}),
                ("تقریباً هیچ‌وقت", {}),
            ],
        },

        # Multiple-choice (checkbox) - at least 2
        {
            "order": 3,
            "type": "multiple",
            "text": "کدام مشکلات زیر را تجربه کرده‌اید؟",
            "choices": [
                ("جوش", {"acne": True}),
                ("قرمزی", {"redness": 2}),
                ("خشکی", {"dryness": 2}),
                ("هیچ‌کدام", {}),
            ],
        },
        {
            "order": 4,
            "type": "multiple",
            "text": "کدام محصولات مراقبت پوستی را استفاده می‌کنید؟",
            "choices": [
                ("مرطوب‌کننده", {"hydration": 2}),
                ("سرم ویتامین‌C", {}),
                ("ماسک صورت", {}),
                ("لایه‌بردار", {"sensitivity": 1}),
            ],
        },

        # Range (slider) - at least 2
        {
            "order": 5,
            "type": "range",
            "text": "میزان چربی پوست خود را از ۰ تا ۱۰ مشخص کنید:",
            "range_effect_map": {
                "0-3": {"dryness": 2},
                "4-7": {"oiliness": 1},
                "8-10": {"oiliness": 3},
            },
        },
        {
            "order": 6,
            "type": "range",
            "text": "روزانه چند لیوان آب می‌نوشید؟ (۰ تا ۱۰)",
            "range_effect_map": {
                "0-3": {"dryness": 1},
                "4-7": {},
                "8-10": {"hydration": 2},
            },
        },

        # Age range (dropdown) - at least 2
        {
            "order": 7,
            "type": "age_range",
            "text": "در چه بازه سنی قرار دارید؟",
            "choices": [
                ("زیر ۱۸", {"age_range": "under_18"}),
                ("۱۸ تا ۲۵", {"age_range": "18-25"}),
                ("۲۵ تا ۳۵", {"age_range": "25-35"}),
                ("بیش از ۳۵", {"age_range": "35+"}),
            ],
        },
        {
            "order": 8,
            "type": "age_range",
            "text": "سن شما در گروه زیر قرار می‌گیرد؟",
            "choices": [
                ("زیر ۳۰", {"age_range": "under_30"}),
                ("۳۰ تا ۴۰", {"age_range": "30-40"}),
                ("۴۰ تا ۵۰", {"age_range": "40-50"}),
                ("۵۰ به بالا", {"age_range": "50+"}),
            ],
        },

        # Scale (Likert) - at least 2
        {
            "order": 9,
            "type": "scale",
            "text": "از ۱ تا ۵، شدت قرمزی پوست خود را ارزیابی کنید:",
            "scale_effect_map": {
                "1": {},
                "2": {"redness": 1},
                "3": {"redness": 2},
                "4": {"redness": 3},
                "5": {"redness": 4},
            },
        },
        {
            "order": 10,
            "type": "scale",
            "text": "از ۱ تا ۵، میزان نرمی پوست خود را ارزیابی کنید:",
            "scale_effect_map": {
                "1": {"dryness": 2},
                "2": {},
                "3": {},
                "4": {"hydration": 1},
                "5": {"hydration": 2},
            },
        },

        # Boolean (Yes/No) - at least 2
        {
            "order": 11,
            "type": "boolean",
            "text": "آیا پوستتان منافذ باز و واضح دارد؟",
            "boolean_effects": {"yes": {"oiliness": 2}, "no": {}},
        },
        {
            "order": 12,
            "type": "boolean",
            "text": "آیا از ضدآفتاب هر روز استفاده می‌کنید؟",
            "boolean_effects": {"yes": {}, "no": {"sensitivity": 1}},
        },

        # Additional to reach 20 total (mix types)
        {
            "order": 13,
            "type": "single",
            "text": "چند ساعت در شب می‌خوابید؟",
            "choices": [
                ("کمتر از ۶ ساعت", {"dryness": 1}),
                ("۶ تا ۸ ساعت", {}),
                ("بیش از ۸ ساعت", {"hydration": 1}),
            ],
        },
        {
            "order": 14,
            "type": "multiple",
            "text": "کدام عوامل زیر باعث تحریک پوست شما می‌شوند؟",
            "choices": [
                ("استرس", {"sensitivity": 1}),
                ("آلودگی هوا", {"sensitivity": 1}),
                ("نور آفتاب", {"redness": 1}),
                ("غذاهای تند", {"redness": 1}),
            ],
        },
        {
            "order": 15,
            "type": "range",
            "text": "در هفته چند بار پوست خود را لایه‌برداری می‌کنید؟",
            "range_effect_map": {"0-1": {"dryness": 1}, "2-3": {}, "4-7": {"sensitivity": 1}},
        },
        {
            "order": 16,
            "type": "age_range",
            "text": "در چه بازه سنی پوستی هستید؟",
            "choices": [
                ("نوجوانی", {"age_range": "teen"}),
                ("جوان", {"age_range": "young"}),
                ("میانسال", {"age_range": "mid"}),
                ("سالمند", {"age_range": "senior"}),
            ],
        },
        {
            "order": 17,
            "type": "scale",
            "text": "از ۱ تا ۵، میزان کشسانی پوست خود را چقدر ارزیابی می‌کنید؟",
            "scale_effect_map": {"1": {"elasticity": 1}, "2": {}, "3": {}, "4": {}, "5": {}},
        },
        {
            "order": 18,
            "type": "boolean",
            "text": "آیا اخیراً تغییر قابل توجهی در وضعیت پوستتان داشته‌اید؟",
            "boolean_effects": {"yes": {"redness": 1}, "no": {}},
        },
        {
            "order": 19,
            "type": "single",
            "text": "پوستتان در فصل زمستان چگونه است؟",
            "choices": [
                ("خشک و پوسته‌پوسته", {"dryness": 3}),
                ("بدون تغییر خاص", {}),
                ("چرب اما بدون مشکلات خاص", {"oiliness": 1}),
            ],
        },
        {
            "order": 20,
            "type": "multiple",
            "text": "در طول روز چند بار پوست خود را لمس می‌کنید؟",
            "choices": [
                ("کمتر از ۵ بار", {}),
                ("۵ تا ۱۰ بار", {"acne": True}),
                ("بیشتر از ۱۰ بار", {"acne": True, "sensitivity": 1}),
            ],
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
