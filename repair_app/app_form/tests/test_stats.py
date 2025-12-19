# app_form/tests/test_stats.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Request
from datetime import date  

User = get_user_model()

class StatsViewTests(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.client = Client()
        
        # Пользователи
        self.client_user = User.objects.create_user(
            username='client1', 
            password='pass123', 
            fio='Иванов И.И.', 
            role='client'
        )
        self.specialist_user = User.objects.create_user(
            username='spec1', 
            password='pass123', 
            fio='Петров П.П.', 
            role='specialist'
        )
        
        # YYYY-MM-DD
        self.completed1 = Request.objects.create(
            client=self.client_user, 
            master=self.specialist_user,
            climate_tech_type='Кондиционер', 
            request_status='completed',
            start_date=date(2025, 12, 1),      
            completion_date=date(2025, 12, 1)  
        )
        self.completed2 = Request.objects.create(
            client=self.client_user, 
            master=self.specialist_user,
            climate_tech_type='Сплит', 
            request_status='completed',
            start_date=date(2025, 12, 2),
            completion_date=date(2025, 12, 2)
        )
    
    def test_stats_completed_count(self):
        """ 2 завершенные заявки"""
        response = self.client.get(reverse('stats'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['completed_count'], 2)
    
    def test_stats_avg_time(self):
        """ Среднее время (delta=0, т.к. даты одинаковые)"""
        response = self.client.get(reverse('stats'))
        self.assertEqual(response.context['avg_hours'], 0)  
    
    def test_stats_types(self):
        """ Статистика по типам"""
        response = self.client.get(reverse('stats'))
        types = {item['climate_tech_type']: item['count'] 
                for item in response.context['type_stats']}
        self.assertEqual(types['Кондиционер'], 1)
        self.assertEqual(types['Сплит'], 1)





