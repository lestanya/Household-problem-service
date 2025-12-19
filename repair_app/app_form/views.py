from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from django.contrib.auth import get_user_model
from .models import Request, Comment
from .forms import UserForm, RequestForm, CommentForm

User = get_user_model()


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']      # username из User
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.fio}!')
            return redirect('dashboard')
        messages.error(request, 'Неверный логин или пароль')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('index')


@login_required
def profile(request):
    user = request.user
    context = {
        'user_role': user.role,
        'user_phone': user.phone,
        'user_fio': user.fio,
    }
    return render(request, 'profile.html', context)


@login_required
def dashboard(request):
    # Фильтрация заявок по роли текущего пользователя
    user = request.user
    role = getattr(user, 'role', None)
    
    if role == 'specialist':
        requests_qs = Request.objects.filter(master=user)
    elif role == 'client':
        requests_qs = Request.objects.filter(client=user)
    else:  # admin, manager, operator
        requests_qs = Request.objects.all()
    
    active_requests = requests_qs.filter(request_status__in=['new', 'in_progress']).count()
    users = User.objects.all()
    comments = Comment.objects.all()

    # Флаг: текущий пользователь — специалист
    is_specialist = role == 'specialist'

    # Инициализируем формы
    user_form = UserForm()
    request_form = RequestForm()
    
    # Форма комментария только для специалистов с ограничением по заявкам
    if is_specialist:
        comment_form = CommentForm()
        # Только заявки текущего специалиста
        comment_form.fields['request'].queryset = requests_qs
        comment_form.fields['request'].empty_label = "Выберите заявку"
    else:
        comment_form = None

    if request.method == 'POST':
        # Защита: комментарии только для специалистов
        if 'comment_submit' in request.POST and is_specialist:
            comment_form = CommentForm(request.POST)
            # Ограничиваем queryset и для POST
            comment_form.fields['request'].queryset = requests_qs
            
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.master = request.user      # текущий специалист
                comment.save()
                messages.success(request, 'Комментарий добавлен!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Выберите заявку и заполните сообщение.')

        elif 'user_submit' in request.POST:
            # Только админы/менеджеры
            if role in ['admin', 'manager']:
                user_form = UserForm(request.POST)
                if user_form.is_valid():
                    user_form.save()
                    messages.success(request, 'Пользователь добавлен!')
                    return redirect('dashboard')

        elif 'request_submit' in request.POST:
            # Клиенты, менеджеры, админы
            if role in ['client', 'manager', 'admin']:
                request_form = RequestForm(request.POST)
                if request_form.is_valid():
                    request_form.save()
                    messages.success(request, 'Заявка добавлена!')
                    return redirect('dashboard')

    context = {
        'users': users,
        'requests': requests_qs,
        'comments': comments,
        'active_requests': active_requests,
        'user_form': user_form,
        'request_form': request_form,
        'comment_form': comment_form,
        'is_specialist': is_specialist,
    }
    return render(request, 'dashboard.html', context)




def qr_survey_page(request):
    """Страница для генерации QR-кода оценки качества"""
    return render(request, 'qr_code.html')


def stats_view(request):
    # Выполненные заявки
    completed_qs = Request.objects.filter(request_status='completed')
    completed_count = completed_qs.count()

    # Среднее время выполнения (completion_date - start_date) в часах
    durations = []
    for r in completed_qs.exclude(completion_date__isnull=True):
        delta = r.completion_date - r.start_date
        durations.append(delta.total_seconds() / 3600)

    avg_hours = 0
    if durations:
        avg_hours = sum(durations) / len(durations)

    # Статистика по типам неисправностей
    type_stats = (
        Request.objects
        .values('climate_tech_type')
        .annotate(count=Count('request_id'))   # ← тут главное изменение
        .order_by('-count')
    )

    context = {
        'completed_count': completed_count,
        'avg_hours': avg_hours,
        'type_stats': type_stats,
    }
    return render(request, 'stats.html', context)