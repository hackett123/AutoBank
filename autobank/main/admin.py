from django.contrib import admin

# Register your models here.

from main.models import Purchase, PurchaseType

admin.site.register(Purchase)
admin.site.register(PurchaseType)
