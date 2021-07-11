from django.contrib import admin

# Register your models here.

from main.models import Purchase, PurchaseType, Shop, Recurring

admin.site.register(Purchase)
admin.site.register(PurchaseType)
admin.site.register(Shop)
admin.site.register(Recurring)

