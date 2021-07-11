from django.db import models
from django.contrib.auth.models import User


class PurchaseType(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    type = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.type)

class Shop(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.name)


class Purchase(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    shop = models.ForeignKey(Shop, related_name="purchases", on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.IntegerField(blank=False)
    bought_for = models.CharField(max_length=200)
    date = models.DateField()

    # acts as a foreign key which lets us query all purchases hashed on purchase type
    purchase_type = models.ForeignKey(PurchaseType, related_name="purchases", on_delete=models.CASCADE)
    purchased_by = models.ForeignKey(User, related_name="purchases", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.amount} of ${self.price} at {self.shop.name} for "{self.description}" by {self.purchased_by.username} on {self.date}'

    def __add__(self, o):
        return self.price + o.price

# subscriptions, rent, etc
class Recurring(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.TextField()
    
    # 1 = yearly, 12 = monthly
    frequency = models.IntegerField()
    bought_for = models.CharField(max_length=200)

    # foreign keys
    purchased_by = models.ForeignKey(User, related_name="subscriptions", on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name="subscriptions", on_delete=models.CASCADE)

    def __str__(self):
        return f'${self.price} / {"year" if self.frequency == 1 else "month" if self.frequency == 12 else str(self.frequency, "times per year")} from {self.shop}'