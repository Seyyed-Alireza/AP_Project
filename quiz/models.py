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

    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES, default=SKIN_TYPE_CHOICES[-1][0])

    acne = models.IntegerField(default=0)
    sensitivity = models.IntegerField(default=0)
    dryness = models.IntegerField(default=0)
    oiliness = models.IntegerField(default=0)
    redness = models.IntegerField(default=0)
    age_range = models.CharField(max_length=20, null=True, blank=True)
    hydration = models.IntegerField(default=0)
    elasticity = models.IntegerField(default=0)

    preferences = models.JSONField(default=list)

    budget_range = models.CharField(max_length=3, choices=BUDGET_CHOICES, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} - پوست"

# class SkinProfileEdit(models.Model):
#     skin_profile = models.ForeignKey(SkinProfile, on_delete=models.CASCADE)
