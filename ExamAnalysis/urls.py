from django.urls import path
from . import views

app_name = 'exam_analysis'  # lowercase for consistency

urlpatterns = [
    path('result/<str:exam_id>/', views.exam_analysis_detail, name='exam_analysis'),    #access for teacher only
    path('result/<str:exam_id>/<str:student_id>/', views.result_analysis_detail, name='result_analysis'), # accesed by student
    path('student/<str:student_id>/', views.student_performance, name='student_analysis'), #accesed by student
]
