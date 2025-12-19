from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from django.contrib.auth import get_user_model
from .models import Request, Comment
from .forms import UserForm, RequestForm, CommentForm, ClientRegistrationForm

User = get_user_model()


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']      
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
def profile_view(request):
    requests = Request.objects.filter(client=request.user)
    
    if request.user.role == 'client':
        if request.method == 'POST' and 'create_request' in request.POST:
            form = RequestForm(request.POST)
            if form.is_valid():
                request_obj = form.save(commit=False)
                request_obj.client = request.user
                request_obj.request_status = 'new'
                request_obj.save()
                messages.success(request, f'✅ Заявка #{request_obj.request_id} создана!')
                return redirect('profile')
        else:
            form = RequestForm()
    else:
        form = None
    
    context = {
        'requests': requests,
        'request_form': form,
        'user': request.user,
        'user_role': request.user.get_role_display(),
        'user_fio': request.user.fio,
        'user_phone': request.user.phone,
    }
    return render(request, 'profile.html', context)


@login_required
def dashboard(request):
    user = request.user
    role = getattr(user, 'role', None)
    
    # Фильтрация заявок по роли
    if role == 'specialist':
        requests_qs = Request.objects.filter(master=user)
    elif role == 'client':
        requests_qs = Request.objects.filter(client=user)
    elif role == 'manager':
        requests_qs = Request.objects.all()
    else:
        requests_qs = Request.objects.all()
    

    is_specialist = role == 'specialist'
    is_manager = role == 'manager'
    is_client = role == 'client'
    user_role = role
    
    specialists = User.objects.filter(role='specialist')
    active_requests = requests_qs.filter(request_status__in=['new', 'in_progress']).count()
    users = User.objects.filter(role__in=['specialist', 'manager']).order_by('fio')
    comments = Comment.objects.all()

   
    user_form = UserForm()
    request_form = RequestForm()
    if is_specialist:
        comment_form = CommentForm()
        comment_form.fields['request'].queryset = requests_qs
    else:
        comment_form = None


    if request.method == 'POST':
        if 'edit_submit' in request.POST:
            request_id = request.POST.get('request_id')
            req = get_object_or_404(Request, request_id=request_id, client=user)
            
            req.climate_tech_type = request.POST.get('climate_tech_type')
            req.climate_tech_model = request.POST.get('climate_tech_model')
            req.description = request.POST.get('description', '')
            req.save()
            
            messages.success(request, f'Заявка #{request_id} успешно обновлена!')
            return redirect('dashboard')
        

        if 'user_submit' in request.POST:
            user_form = UserForm(request.POST)
            if user_form.is_valid():
                user_obj = user_form.save()
                messages.success(request, f'Пользователь {user_obj.fio} создан!')
                user_form = UserForm()  # Сброс формы
            else:
                messages.error(request, 'Ошибка создания пользователя!')
        
        #  АДМИН/ОПЕРАТОР СОЗДАЕТ ЗАЯВКУ
        if 'request_submit' in request.POST:
            request_form = RequestForm(request.POST)
            if request_form.is_valid():
                req_obj = request_form.save(commit=False)
                req_obj.client = user  # Клиент = текущий пользователь
                req_obj.save()
                messages.success(request, f'Заявка #{req_obj.request_id} создана!')
                request_form = RequestForm()  # Сброс формы
            else:
                messages.error(request, 'Ошибка создания заявки!')
        
        #  СПЕЦИАЛИСТ ДОБАВЛЯЕТ КОММЕНТАРИЙ
        if 'comment_submit' in request.POST and is_specialist:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.master = user
                comment.save()
                messages.success(request, 'Комментарий добавлен!')
                comment_form = CommentForm()
                comment_form.fields['request'].queryset = requests_qs
            else:
                messages.error(request, 'Ошибка добавления комментария!')

    context = {
        'users': users, 
        'requests': requests_qs, 
        'comments': comments,
        'active_requests': active_requests, 
        'user_form': user_form,
        'request_form': request_form, 
        'comment_form': comment_form,
        'is_specialist': is_specialist, 
        'is_manager': is_manager,
        'is_client': is_client,
        'user_role': user_role,
        'specialists': specialists,
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
        .annotate(count=Count('request_id'))   
        .order_by('-count')
    )

    context = {
        'completed_count': completed_count,
        'avg_hours': avg_hours,
        'type_stats': type_stats,
    }
    return render(request, 'stats.html', context)


@login_required
def status_change(request, request_id):
    # Только специалисты
    if getattr(request.user, 'role', None) != 'specialist':
        messages.error(request, 'Только специалисты могут менять статус!')
        return redirect('dashboard')
    
    # Получаем заявку
    req = get_object_or_404(Request, request_id=request_id, master=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('request_status')
        
        # Проверяем, что статус валидный
        valid_statuses = ['new', 'in_progress', 'ready', 'completed']
        if new_status in valid_statuses:
            req.request_status = new_status
            req.save()
            messages.success(request, f'Статус заявки #{request_id} изменён на "{new_status}"')
        else:
            messages.error(request, 'Неверный статус!')
        
        return redirect('dashboard')
    
   
    context = {
        'request': req,
        'status_choices': Request.STATUS_CHOICES,
    }
    return render(request, 'status_change.html', context)


@login_required
@require_http_methods(["POST"])
def api_status_change(request):
    if getattr(request.user, 'role', None) != 'specialist': return JsonResponse({'success': False}, status=403)
    req = get_object_or_404(Request, request_id=request.POST['request_id'], master=request.user)
    req.request_status = request.POST['request_status']
    req.save()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def api_assign_master(request):
    if getattr(request.user, 'role', None) != 'manager': return JsonResponse({'success': False}, status=403)
    req = get_object_or_404(Request, request_id=request.POST['request_id'])
    req.master = User.objects.get(id=request.POST['master_id'])
    req.request_status = 'in_progress'
    req.save()
    return JsonResponse({'success': True})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'✅ Добро пожаловать, {user.fio}!')
            return redirect('dashboard')
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'register.html', {'form': form})



