from django.urls import path
from . import views

app_name = 'exam_conduct'

urlpatterns = [
    path('', views.exam_entry, name='exam_entry'),
    path('session/<uuid:session_id>/', views.exam_interface, name='exam_interface'),
    path('session/<uuid:session_id>/submit/', views.submit_exam, name='submit_exam'),
    path('session/<uuid:session_id>/proctoring/', views.proctoring_alert, name='proctoring_alert'),
]
