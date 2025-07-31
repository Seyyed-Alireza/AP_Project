from django.db import models
from django.contrib.auth.models import User

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
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    value = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - پاسخ به سوال {self.question.order}"

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

    age_range = models.CharField(max_length=20, null=True, blank=True)

    preferences = models.JSONField(default=list, blank=True)

    budget_range = models.CharField(max_length=3, choices=BUDGET_CHOICES, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} - پوست"
