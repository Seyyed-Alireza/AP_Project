from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
class SkinProfile(models.Model):
    
    SKIN_TYPE_CHOICES = [
        ('dry', 'خشک'),
        ('oily', 'چرب'),
        ('sensitive', 'حساس'),
        ('combination', 'مختلط'),
        ('normal', 'نرمال'),
    ]

    BUDGET_CHOICES = [
        ('$', 'ارزان'),
        ('$$', 'متوسط'),
        ('$$$', 'گران'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    quiz_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    quiz_skipped = models.BooleanField(default=False)

    skin_type = MultiSelectField(choices=SKIN_TYPE_CHOICES, max_length=50)
    
    SKIN_FEATURES = [
        ('acne', 'آکنه'),
        ('sensitivity', 'حساسیت'),
        ('dryness', 'خشکی'),
        ('oiliness', 'چربی'),
        ('redness', 'قرمزی'),
        ('hydration', 'آبرسانی'),
        ('elasticity', 'کشسانی'),
    ]

    SKIN_PROPERTIES = [
        ('acne', 'Acne'),
        ('sensitivity', 'Sensitivity'),
        ('dryness', 'Dryness'),
        ('oiliness', 'Oiliness'),
        ('redness', 'Redness'),
        ('hydration', 'Hydration'),
        ('elasticity', 'Elasticity')
    ]

    acne = models.IntegerField(default=0)
    sensitivity = models.IntegerField(default=0)
    dryness = models.IntegerField(default=0)
    oiliness = models.IntegerField(default=0)
    redness = models.IntegerField(default=0)
    hydration = models.IntegerField(default=0)
    elasticity = models.IntegerField(default=0)

    def get_skin_scores(self):
        return [
            ('acne', self.acne),
            ('sensitivity', self.sensitivity),
            ('dryness', self.dryness),
            ('oiliness', self.oiliness),
            ('redness', self.redness),
            ('hydration', self.hydration),
            ('elasticity', self.elasticity),
        ]


    def get_skin_scores_for_search(self):
        return [
            ('آکنه', self.acne),
            ('حساس', self.sensitivity),
            ('خشکی', self.dryness),
            ('چربی زیاد', self.oiliness),
            ('قرمزی', self.redness),
            ('آبرسان', self.hydration),
            ('elasticity', self.elasticity),
        ]


    def set_skin_scores(self, values):
        (
            self.acne,
            self.sensitivity,
            self.dryness,
            self.oiliness,
            self.redness,
            self.hydration,
            self.elasticity,
        ) = values
        
    # def auto_detect_skin_type(self):
        # oil = self.oiliness
        # dry = self.dryness
        # sensitive = self.sensitivity
        # if oil >= 7 and dry <= 3:
        #     self.skin_type = 'oily'
        # elif dry >= 7 and oil <= 3:
        #     self.skin_type = 'dry'
        # elif oil >= 5 and dry >= 5:
        #     self.skin_type = 'combination'
        # elif sensitive >= 7:
        #     self.skin_type = 'sensitive'
        # else:
        #     self.skin_type = 'normal'
    def auto_detect_skin_type(self):
        skin_types = []

        # حساس
        if self.sensitivity >= 4 or self.redness >= 4:
            skin_types.append("sensitive")

        # خشک
        if self.dryness >= 4 and self.oiliness <= 2:
            skin_types.append("dry")

        # چرب
        if self.oiliness >= 4 and self.dryness <= 2:
            skin_types.append("oily")

        # مختلط
        if (
            self.oiliness >= 3
            and self.dryness >= 3
            and abs(self.oiliness - self.dryness) <= 2
        ):
            skin_types.append("combination")

        # نرمال
        if not skin_types:
            skin_types.append("normal")
        
        if "combination" in skin_types:
            skin_types = [t for t in skin_types if t not in ["dry", "oily"]]

        self.skin_type = skin_types
        return skin_types




    age_range = models.CharField(max_length=20, null=True, blank=True)

    preferences = models.JSONField(default=list, blank=True)

    budget_range = models.CharField(max_length=3, choices=BUDGET_CHOICES, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} - پوست"


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creatd_at = models.DateTimeField(auto_now_add=True)
class Question(models.Model):
    TEXT_CHOICES = [
        ('single', 'تک‌گزینه‌ای (Radio button)'),
        ('multiple', 'چندگزینه‌ای (Checkbox)'),
        ('range', 'مقدار عددی (Slider)'),
        ('age_range', 'محدوده سنی (Dropdown)'),
        ('scale', 'مقیاس 1 تا 5 (Likert scale)'),
        ('boolean', 'بله / خیر (Yes/No)'),
    ]

    text = models.TextField()
    order = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=TEXT_CHOICES, default='single')
    subject = models.CharField(max_length=20, choices=SkinProfile.SKIN_PROPERTIES, blank=True)

    def __str__(self):
        return f"{self.order}. {self.text}"
    
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    effects = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    value = models.CharField(max_length=100, blank=True, null=True)
    do_not_now = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - پاسخ به سوال {self.question.order}"

