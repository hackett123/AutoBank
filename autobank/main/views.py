from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from main.models import PurchaseType, Purchase, Recurring, Shop
from django.contrib.auth.decorators import login_required

import csv
import time
from django.http import HttpResponse
from datetime import date

# Create your views here.


def splash(request):
    if request.user.is_authenticated:
        types = PurchaseType.objects.all()
        shops = Shop.objects.all()
        return render(request, 'home.html', {'user': request.user, 'purchase_types': types, 'shops': shops})
    return render(request, "splash.html", {})

def stats(request):
    if request.user.is_authenticated:
        types = PurchaseType.objects.all()
        shops = Shop.objects.all()

        # make dictionaries of (category) -> (sum price) for both dimensions of data
        type_sum_prices = {purchase_type:sum([purchase.price for purchase in list(purchase_type.purchases.all())]) for purchase_type in types}
        shop_sum_prices = {shop:sum([purchase.price for purchase in list(shop.purchases.all())]) for shop in shops}

        return render(request, 'stats.html', {'purchase_types': types, 'shops': shops, 'type_sum_prices': type_sum_prices, 'shop_sum_prices': shop_sum_prices})
    return render(request, "splash.html", {})


def login_(request):
    if request.method == "POST":
        print("LOGGING IN")
        user = authenticate(username=request.POST.get(
            'username'), password=request.POST.get('password'))
        print(user)
        if user is not None:
            print("LOGGED IN")
            login(request, user)
            return redirect("/")
        print("COULD NOT FIND USER")
    return render(request, "login.html", {})


def logout_(request):
    logout(request)
    return redirect("/")

@login_required
def add_recurring(request):
    if request.method == 'POST':
        recurring = Recurring.objects.create(
            price=request.POST['price'],
            shop=Shop.objects.get(name=request.POST['shop']),
            description=request.POST['description'],
            bought_for=request.POST['for_choices'],
            purchased_by=User.objects.get(username=request.user),
            frequency=request.POST['frequency']
        )
        recurring.save()
    return redirect('/')

@login_required
def add_purchase(request):
    if request.method == 'POST':
        purchase_type = request.POST.getlist("type_choices")[0]

        print(f'purchase_type received is {purchase_type}')
        purchase_type_obj = PurchaseType.objects.get(type=purchase_type)
        print(f'object found is {purchase_type_obj}')
        print(f'Creating purchase with fields {request.POST["price"]}', 
            f'{request.POST["shop"]}, {request.POST["description"]}, {request.POST["amount"]}', purchase_type_obj, User.objects.get(username=request.user))

        # if amount is null default to 1
        amount = request.POST['amount'] if request.POST['amount'] else 1
        dt = request.POST['date'] if request.POST['date'] else date.today()

        purchase = Purchase.objects.create(
            price=request.POST['price'],
            shop=Shop.objects.get(name=request.POST['shop']),
            date=dt,
            description=request.POST['description'],
            amount=amount,
            bought_for=request.POST['for_choices'],
            purchase_type=purchase_type_obj,
            purchased_by=User.objects.get(username=request.user)
        )

        purchase.save()
        return redirect('/')
    else: return redirect('/')

@login_required
def new_purchase_type(request):
    if request.method == 'POST':
        if request.POST['type']:
            new_type = PurchaseType.objects.create(type=request.POST['type'])
            new_type.save()
    return redirect('/')

@login_required
def new_shop(request):
    if request.method == 'POST':
        if request.POST['shop']:
            new_shop = Shop.objects.create(name=request.POST['shop'])
            new_shop.save()
    return redirect('/')

from django.template.defaulttags import register

# django filter shit
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)