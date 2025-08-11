from django.urls import path
from .views import skin_quiz_view, skin_quiz_view_prof, from_prof, skip_quiz

urlpatterns = [
    path('', skin_quiz_view, name='quiz'),
    path('prof', skin_quiz_view_prof, name='quiz_prof'),
    path('q_f_prof', from_prof, name='quiz_from_prof'),
    path('skip', skip_quiz, name='skip_quiz')
]
