from django.urls import path
from . import views

urlpatterns = [
    path('', views.genQ, name='genQ'),
    path('submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path('saveQuiz/', views.save_quiz, name='save_quiz'),
]
