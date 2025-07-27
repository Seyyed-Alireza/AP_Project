from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class RoutinePlan(models.Model):

    PLAN_NAMES = [
        ('full', 'Full Routine'),
        ('hydration', 'Hydration Plan'),
        ('acne', 'Anti-Acne Routine'),
        ('brightening', 'Brightening Plan'),
        ('anti_aging', 'Anti-Aging Routine'),
        ('sensitive', 'Sensitive Skin Routine'),
        ('minimal', 'Minimal Routine'),
        ('oily', 'Oily Skin Plan'),
        ('morning', 'Morning Routine'),
        ('night', 'Night Routine'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routine_plans')
    plan_name = models.CharField(max_length=100, choices=PLAN_NAMES, default=PLAN_NAMES[0][0])
    steps = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan_name} ({self.user.username})"