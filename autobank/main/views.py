from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from main.models import PurchaseType, Purchase
from django.contrib.auth.decorators import login_required

import csv
import time
from django.http import HttpResponse

# Create your views here.


def splash(request):
    if request.user.is_authenticated:
        types = PurchaseType.objects.all()
        return render(request, 'home.html', {'user': request.user, 'purchase_types': types})
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
def add_purchase(request):
    if request.method == 'POST':
        bought_for = request.POST.getlist("for_choices")[0]
        purchase_type = request.POST.getlist("type_choices")[0]

        print(f'purchase_type received is {purchase_type}')
        purchase_type_obj = PurchaseType.objects.get(type=purchase_type)
        print(f'object found is {purchase_type_obj}')
        print(f'Creating purchase with fields {request.POST["price"]}', 
            f'{request.POST["shop"]}, {request.POST["description"]}, {request.POST["amount"]}', bought_for, purchase_type_obj, User.objects.get(username=request.user))


        purchase = Purchase.objects.create(
            price=request.POST['price'],
            shop=request.POST['shop'],
            description=request.POST['description'],
            amount=request.POST['amount'],
            bought_for=bought_for,
            purchase_type=purchase_type_obj,
            purchased_by=User.objects.get(username=request.user)
        )

        purchase.save()
        return redirect('/')
    else: return redirect('/')
