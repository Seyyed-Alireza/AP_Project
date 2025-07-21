from django import forms
from .models import Question, Choice

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = Question.objects.all().order_by('order')
        for question in questions:
            choices = [(c.id, c.text) for c in question.choices.all()]
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )
