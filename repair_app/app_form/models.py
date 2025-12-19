from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings



class User(AbstractUser):
    """
    Кастомный пользователь системы:
    логин/пароль берутся из AbstractUser:
    - username
    - password (хранится как хеш)
    Плюс свои поля: ФИО, телефон, роль.
    """
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('specialist', 'Специалист'),
        ('operator', 'Оператор'),
        ('client', 'Заказчик'),
    ]

    fio = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f'{self.fio} ({self.username}, {self.role})'
    

class Request(models.Model):
    """
    Заявка на ремонт климатического оборудования.
    """
    STATUS_CHOICES = [
        ('new', 'Новая заявка'),
        ('in_progress', 'В процессе ремонта'),
        ('ready', 'Готова к выдаче'),
        ('completed', 'Завершена'),
    ]

    request_id = models.AutoField(primary_key=True)  
    start_date = models.DateField()                  
    climate_tech_type = models.CharField(max_length=50)   
    climate_tech_model = models.CharField(max_length=100) 
    problem_description = models.TextField()              
    request_status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,   
    )
    completion_date = models.DateField(null=True, blank=True)  
    repair_parts = models.TextField(blank=True)           #  (описание заказанных деталей)

    # masterID и clientID
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='requests_as_master',
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requests_as_client',
    )

    def __str__(self):
        return f'Заявка #{self.request_id} ({self.climate_tech_type}, {self.request_status})'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    message = models.TextField()

    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий #{self.comment_id} к заявке #{self.request.request_id}'

