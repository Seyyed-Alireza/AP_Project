from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import QuizForm
from django.contrib.auth.decorators import login_required
from .models import Choice, SkinProfile, Question, Answer
from django.utils import timezone

@login_required
def skin_quiz_view(request):
    if request.user.skinprofile.quiz_skipped:
        return redirect('mainpage')

    questions = Question.objects.prefetch_related('choices').order_by('order')

    if request.method == 'POST':
        Answer.objects.filter(user=request.user).delete()
        total_effects = {
            'acne': 0,
            'sensitivity': 0,
            'dryness': 0,
            'oiliness': 0,
            'redness': 0,
            'age_range': None,
            'hydration': 0,
            'elasticity': 0,
        }
    
        skin_profile = request.user.skinprofile
        if questions[0]:
            qid = f"question_{questions[0].id}"
            raw_value = request.POST.get(qid)
            choice = Choice.objects.get(id=int(raw_value))
            skin_profile.skin_type = choice.effects['skin_type']
            print(choice.effects['skin_type'])
            # print(choice)

        for question in questions[1:]:
            qid = f"question_{question.id}"
            raw_value = request.POST.getlist(qid) if question.type == "multiple" else request.POST.get(qid)
            if not raw_value:
                continue

            answer = Answer.objects.create(user=request.user, question=question)
            choices = []
            if question.type in ['single', 'age_range', 'scale', 'boolean', 'range']:
                try:
                    choice = Choice.objects.get(id=int(raw_value))
                    choices = [choice]
                    answer.selected_choices.add(choice)
                except:
                    choices = Choice.objects.filter(question=question, text__iexact=str(raw_value))
                    answer.value = str(raw_value)
            elif question.type == 'multiple':
                try:
                    ids = list(map(int, raw_value))
                    choices = Choice.objects.filter(id__in=ids, question=question)
                    answer.selected_choices.set(choices)
                except:
                    continue

            for choice in choices:
                for key, value in choice.effects.items():
                    if isinstance(value, bool):
                        total_effects[key] = total_effects.get(key, False) or value
                    elif isinstance(value, int):
                        total_effects[key] = total_effects.get(key, 0) + value
                    elif isinstance(value, str):
                        total_effects[key] = value

        skin_profile.acne = total_effects.get("acne", 0)
        skin_profile.sensitivity = total_effects.get("sensitivity", 0)
        skin_profile.dryness = total_effects.get("dryness", 0)
        skin_profile.oiliness = total_effects.get("oiliness", 0)
        skin_profile.redness = total_effects.get("redness", 0)
        skin_profile.age_range = total_effects.get('age_range', None)
        skin_profile.quiz_skipped = True
        skin_profile.quiz_completed = True
        if not skin_profile.completed_at:
            skin_profile.completed_at = timezone.now()
        skin_profile.hydration = total_effects.get("hydration", 0)
        skin_profile.elasticity = total_effects.get("elasticity", 0)

        skin_profile.save()
        return redirect('profile')
    elif request.method == 'GET':
        questions = Question.objects.prefetch_related('choices').order_by('order')
        answers = Answer.objects.filter(user=request.user)
        initial_answers = {}

        for answer in answers:
            qid = f"question_{answer.question.id}"
            if answer.question.type == 'multiple':
                initial_answers[qid] = list(answer.selected_choices.values_list('id', flat=True))
            elif answer.question.type in ['single', 'age_range', 'scale', 'boolean', 'range']:
                selected = answer.selected_choices.first()
                if selected:
                    initial_answers[qid] = selected.id
                elif answer.value:
                    initial_answers[qid] = answer.value

        context = {
            'questions': questions,
            'initial_answers': initial_answers
        }
        # print(initial_answers)
        return render(request, 'quiz/quiz.html', context)


    return render(request, 'quiz/quiz.html', {'questions': questions})

def from_prof(request):
    skin_prof = get_object_or_404(SkinProfile, user=request.user)
    skin_prof.quiz_skipped = False
    skin_prof.save()
    return redirect('quiz')

def skip_quiz(request):
    if request.method == "POST":
        profile = get_object_or_404(SkinProfile, user=request.user)
        profile.quiz_skipped = True
        profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=100)

# def skip_quiz(request):
#     if request.method == "POST":
#         profile = get_object_or_404(SkinProfile, user=request.user)
#         profile.quiz_skipped = True
#         profile.save()
#     return redirect('mainpage')