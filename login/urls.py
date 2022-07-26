"""login URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path,include
from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('home',views.home,name='home'),
    path('signup',views.signup,name='signup'),
    path('login',views.handlelogin,name='handlelogin'),
    path('logout',views.handlelogout,name='handlelogout'),
    path('allotment',views.allotment,name='allotment'),
    path('shiftSheet',views.shiftSheet,name='shiftSheet'),
    path('replacement',views.replacement,name='replacement'),
    path('countsub',views.countsub,name='countsub'),
    path('allmembers',views.allmembers,name='allmembers'),
    path('approval',views.approval,name='approval'),
    path('approval/<str:slug>',views.disapproval,name='disapproval'),
    path('userpanel',views.userpanel,name='userpanel'),
    path('usershiftcheck',views.usershiftcheck,name='usershiftcheck'),
    path('teamwisesheet',views.teamwisesheet,name='teamwisesheet'),
]
