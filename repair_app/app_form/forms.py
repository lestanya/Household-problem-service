from django import forms
from django.contrib.auth import get_user_model
from .models import User, Request, Comment


User = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'fio', 'phone', 'role']
        widgets = {
            'role': forms.Select(choices=User.ROLE_CHOICES),
        }

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['start_date', 'climate_tech_type', 'climate_tech_model', 
                 'problem_description', 'request_status', 'completion_date', 
                 'repair_parts', 'master', 'client']
        widgets = {
            'problem_description': forms.Textarea(attrs={'rows': 3}),
            'repair_parts': forms.Textarea(attrs={'rows': 2}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message', 'request']  # ← ЯВНО укажи оба поля
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Введите текст комментария...',
                'class': 'form-control'
            }),
            'request': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'message': 'Комментарий',
            'request': 'Заявка',
        }