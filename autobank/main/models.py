from django.db import models
from django.contrib.auth.models import User


class PurchaseType(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    type = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.type)


class Purchase(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    shop = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.IntegerField(blank=False)
    bought_for = models.CharField(choices=[('MICHELLE', 'just michelle'), (
        'MICHAEL', 'just michael'), ('BOTH', 'both of us')], max_length=200)
    date = models.DateTimeField(auto_created=True, auto_now=True)

    # acts as a foreign key which lets us query all purchases hashed on purchase type
    purchase_type = models.ForeignKey(PurchaseType, related_name="purchases", on_delete=models.CASCADE)
    purchased_by = models.ForeignKey(User, related_name="purchases", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.amount} of ${self.price} at {self.shop} for {self.description} on {self.date}'
