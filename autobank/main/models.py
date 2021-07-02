from django.db import models
from django.contrib.auth.models import User


class PurchaseType(models.Model):
    choices = [
        ('EAT_OUT', 'eating out'),
        ('HOUSE_SUPPLIES', 'small house item purchase'),
        ('TAKE_OUT', 'take out'),
        ('COFFEE', 'coffee')
    ]
    type = models.CharField(choices=choices, max_length=200)


class Purchase(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=10)
    shop = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.IntegerField(blank=False)
    bought_for = models.CharField(choices=[('MICHELLE', 'just michelle'), (
        'MICHAEL', 'just michael'), ('BOTH', 'both of us')], max_length=200)
    date = models.DateTimeField(auto_created=True, auto_now=True)
    purchase_type = models.ForeignKey(PurchaseType, related_name="purchase_type", on_delete=models.CASCADE)
    purchased_by = models.ForeignKey(User, related_name="purchased_by", on_delete=models.CASCADE)
