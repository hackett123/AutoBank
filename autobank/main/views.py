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
        return render(request, 'home.html', {'user': request.user})
        # print(Course.objects.all())
        # ta_course_ids = request.user.TA_courses.all()
        # ta_courses = Course.objects.filter(id__in=ta_course_ids)

        # instructor_course_ids = request.user.instructor_courses.all()
        # instructor_courses = Course.objects.filter(id__in=instructor_course_ids)

        # student_course_ids = request.user.student_courses.all()
        # student_courses = Course.objects.filter(id__in=student_course_ids)
        # # courses = [course for course in Course.objects.all() if request.user ==
        # #            course.instructor or request.user in course.students.all() or request.user in course.ta_staff.all()]
        # return render(request, "home.html", {"user": request.user, "ta_courses": ta_courses, "instructor_courses": instructor_courses, "student_courses": student_courses})
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

        purchase = Purchase.objects.create(
            price=request.POST['price'],
            shop=request.POST['shop'],
            description=request.POST['description'],
            amount=request.POST['amount'],
            bought_for=bought_for,
            purchase_type=purchase_type,
            purchased_by=User.objects.get(username=request.user)
        )
        return redirect('')
    else: return redirect('')
