from django.db import models

from django.db import models


class User(models.Model):
    """
    Пользователь системы: менеджер, специалист, оператор, заказчик.
    type = роль пользователя.
    """
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('specialist', 'Специалист'),
        ('operator', 'Оператор'),
        ('client', 'Заказчик'),
    ]

    user_id = models.AutoField(primary_key=True)  # userID из файла
    fio = models.CharField(max_length=100)       # fio
    phone = models.CharField(max_length=20)      # phone
    login = models.CharField(max_length=50, unique=True)   # login
    password = models.CharField(max_length=128)            
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f'{self.fio} ({self.role})'


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

    request_id = models.AutoField(primary_key=True)  # requestID
    start_date = models.DateField()                  # startDate
    climate_tech_type = models.CharField(max_length=50)   # climateTechType
    climate_tech_model = models.CharField(max_length=100) # climateTechModel
    problem_description = models.TextField()              # problemDescryption
    request_status = models.CharField(max_length=20)      # requestStatus (можно привязать к STATUS_CHOICES)
    completion_date = models.DateField(null=True, blank=True)  # completionDate
    repair_parts = models.TextField(blank=True)           # repairParts (описание заказанных деталей)

    # masterID и clientID
    master = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='requests_as_master'
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requests_as_client'
    )

    def __str__(self):
        return f'Заявка #{self.request_id} ({self.climate_tech_type}, {self.request_status})'


class Comment(models.Model):
    """
    Комментарий специалиста к заявке.
    """
    comment_id = models.AutoField(primary_key=True)  # commentID
    message = models.TextField()                     # message

    master = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )                                                # masterID

    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='comments'
    )                                                # requestID

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий #{self.comment_id} к заявке #{self.request.request_id}'

