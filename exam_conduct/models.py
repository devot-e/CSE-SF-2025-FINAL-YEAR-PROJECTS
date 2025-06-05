from django.db import models
from results.models import Exam, Result, Student
import uuid

class ExamSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    warnings = models.PositiveIntegerField(default=0)
    fullscreen_exits = models.PositiveIntegerField(default=0)
    tab_switches = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Session {self.session_id} for {self.student.name}"
