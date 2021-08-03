"""autobank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from main.views import add_recurring, splash, login_, logout_, add_purchase, new_purchase_type, add_purchase_type_or_shop, new_shop, see_stats, stats, joint_stats, add_inter_payment, add_paycheck
from django.urls import path # avoid regex

urlpatterns = [
    path('admin/', admin.site.urls),
    # add our paths here
    path('', splash),
    path("login", login_, name="login"),
    path("logout", logout_, name="logout"),
    path('add_purchase', add_purchase, name='add_purchase'),
    path('add_recurring', add_recurring, name='add_recurring'),
    path('add_purchase_type_or_shop', add_purchase_type_or_shop, name='add_purchase_type_or_shop'),
    path('new_purchase_type', new_purchase_type, name='new_purchase_type'),
    path('new_shop', new_shop, name='new_shop'),
    path('see_stats', see_stats, name='see_stats'),
    path('stats', stats, name='stats'),
    path('joint_stats', joint_stats, name='joint_stats'),
    path('add_inter_payment', add_inter_payment, name='add_inter_payment'),
    path('add_paycheck', add_paycheck, name='add_paycheck'),
]
