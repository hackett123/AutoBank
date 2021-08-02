from django.contrib import admin

# Register your models here.

from main.models import Purchase, PurchaseType, Shop, Recurring, InterPayment, Paycheck

admin.site.register(Purchase)
admin.site.register(PurchaseType)
admin.site.register(Shop)
admin.site.register(Recurring)
admin.site.register(InterPayment)
admin.site.register(Paycheck)
