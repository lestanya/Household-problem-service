from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import User as CustomUser, Request, Comment
from .forms import UserForm, RequestForm, CommentForm



def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('dashboard')
        messages.error(request, 'Неверный логин или пароль')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('index')

@login_required
def profile(request):
    # Получаем роль пользователя из CustomUser
    try:
        custom_user = CustomUser.objects.get(login=request.user.username)
        user_role = custom_user.role
        user_phone = custom_user.phone
    except:
        user_role = 'Неизвестно'
        user_phone = 'Не указан'
    
    context = {
        'user_role': user_role,
        'user_phone': user_phone,
    }
    return render(request, 'profile.html', context)

@login_required
def dashboard(request):
    # ФИЛЬТРАЦИЯ ПО РОЛЯМ!
    custom_user = CustomUser.objects.get(login=request.user.username)
    role = custom_user.role
    
    if role == 'specialist':
        requests = Request.objects.filter(master=custom_user)
    elif role == 'client':
        requests = Request.objects.filter(client=custom_user)
    else:  # manager, operator
        requests = Request.objects.all()



def dashboard(request):
    users = User.objects.all()
    requests = Request.objects.all()
    comments = Comment.objects.all()

    # Инициализируем ВСЕ формы в начале
    user_form = UserForm()
    request_form = RequestForm()
    comment_form = CommentForm()

    if request.method == 'POST':
        if 'user_submit' in request.POST:
            user_form = UserForm(request.POST)  # Пересоздаем только эту
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Пользователь добавлен!')
                return redirect('dashboard')

        elif 'request_submit' in request.POST:
            request_form = RequestForm(request.POST)
            if request_form.is_valid():
                request_form.save()
                messages.success(request, 'Заявка добавлена!')
                return redirect('dashboard')

        elif 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment_form.save()
                messages.success(request, 'Комментарий добавлен!')
                return redirect('dashboard')

    context = {
        'users': users,
        'requests': requests,
        'comments': comments,
        'user_form': user_form,
        'request_form': request_form,
        'comment_form': comment_form,
        'messages': messages.get_messages(request),
    }
    return render(request, 'dashboard.html', context)
