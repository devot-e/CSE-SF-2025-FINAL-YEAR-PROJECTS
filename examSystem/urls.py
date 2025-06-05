"""
URL configuration for examSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.shortcuts import redirect
from django.urls import path, include
from user_accounts.views import dashboard
from generate_exam.views import delete_exam
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('user_accounts.urls')),
    path('generate_exam/', include('generate_exam.urls')),
    path('dashboard/',dashboard,name='dashboard'),
    path('delete_exam/<str:exam_id>/', delete_exam, name='delete_exam'),
    path('', lambda request: redirect('login')),
    path('exam/', include('exam_conduct.urls')),
    path('analysis/',include('ExamAnalysis.urls'))
    # path('', include('user_accounts.urls')),  # This will make the login page the default landing page
]
