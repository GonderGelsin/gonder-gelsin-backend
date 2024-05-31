# Create your models here.
from django.db import models

from authentication.models import CustomUser


class Order(models.Model):
    status_choices = [
        ('P', 'Pending'),
        ('O', 'Ongoing'),
        ('C', 'Completed'),
    ]
    vehicle_choices = [
        ('M', 'Motorcycle'),
        ('C', 'Car'),
    ]
    payment_choices = [
        ('CC', 'Credit Card'),
        ('CS', 'Cash'),
    ]
    status = models.CharField(max_length=1, choices=status_choices, default='P')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post_content = models.TextField()
    departure_address = models.CharField(max_length=100)
    arrival_address = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=1, choices=vehicle_choices)
    weight_limit = models.FloatField()
    payment_method = models.CharField(max_length=2, choices=payment_choices)
