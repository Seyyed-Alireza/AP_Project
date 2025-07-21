from django.contrib import admin
from .models import Choice, Question, SkinProfile, Answer

admin.site.register(Choice)
admin.site.register(SkinProfile)
admin.site.register(Question)
admin.site.register(Answer)
