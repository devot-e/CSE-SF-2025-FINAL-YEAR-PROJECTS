from django import forms
from results.models import Exam

class ExamAccessForm(forms.Form):
    exam_id = forms.CharField(
        label='Exam ID',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your exam ID',
            'class': 'form-control'
        })
    )
