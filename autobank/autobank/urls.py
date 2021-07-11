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

from main.views import add_recurring, splash, login_, logout_, add_purchase, new_purchase_type, new_shop, stats
from django.urls import path # avoid regex

urlpatterns = [
    path('admin/', admin.site.urls),
    # add our paths here
    path('', splash),
    path("login", login_, name="login"),
    path("logout", logout_, name="logout"),
    path('add_purchase', add_purchase, name='add_purchase'),
    path('add_recurring', add_recurring, name='add_recurring'),
    path('new_purchase_type', new_purchase_type, name='new_purchase_type'),
    path('new_shop', new_shop, name='new_shop'),
    path('stats', stats, name='stats'),
]
