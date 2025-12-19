from django import forms
from django.contrib.auth import get_user_model
from .models import User, Request, Comment
from django.contrib.auth.forms import UserCreationForm


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
        fields = ['message', 'request'] 
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

class ClientRegistrationForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ['fio', 'phone', 'username', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Красивые стили для всех полей
        self.fields['fio'].widget.attrs.update({
            'placeholder': 'Иванов Иван Иванович',
            'autocomplete': 'name'
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': '+7 (999) 123-45-67',
            'autocomplete': 'tel'
        })
        self.fields['username'].widget.attrs.update({
            'placeholder': 'мой_логин'
        })
      
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'  
        if commit:
            user.save()
        return user
    

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['climate_tech_type', 'climate_tech_model', 'problem_description', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'climate_tech_type': forms.TextInput(attrs={
                'placeholder': 'Кондиционер, сплит-система...'
            }),
            'climate_tech_model': forms.TextInput(attrs={
                'placeholder': 'Daikin FTXM25R, LG PC12SQ...'
            }),
            'problem_description': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Подробно опишите проблему...'
            }),
        }
        labels = {
            'climate_tech_type': 'Тип оборудования',
            'climate_tech_model': 'Модель',
            'problem_description': 'Описание проблемы', 
            'start_date': 'Дата обращения'
        }