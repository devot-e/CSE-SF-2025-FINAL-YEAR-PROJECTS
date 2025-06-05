from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
import datetime

# Create your models here.

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    teacher_id = models.CharField(max_length=20, unique=True, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if not self.teacher_id:
            # Get the current year
            year = datetime.datetime.now().year
            # Get the last teacher ID for this year
            last_id = Teacher.objects.filter(teacher_id__startswith=f'T{year}').aggregate(Max('teacher_id'))['teacher_id__max']

            if last_id:
                # Extract the number and increment
                last_number = int(last_id[5:])
                new_number = last_number + 1
            else:
                # First teacher of the year
                new_number = 1

            # Format: T2024001
            self.teacher_id = f'T{year}{new_number:03d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.teacher_id})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if not self.student_id:
            # Get the current year
            year = datetime.datetime.now().year
            # Get the last student ID for this year
            last_id = Student.objects.filter(student_id__startswith=f'S{year}').aggregate(Max('student_id'))['student_id__max']

            if last_id:
                # Extract the number and increment
                last_number = int(last_id[5:])
                new_number = last_number + 1
            else:
                # First student of the year
                new_number = 1

            # Format: S2024001
            self.student_id = f'S{year}{new_number:03d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

class Exam(models.Model):
    exam_id = models.CharField(max_length=20, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    quiz_questions = models.JSONField(default=dict)   # This will store the exam paper data it's a list of dictionaries

    def __str__(self):
        return f"Exam {self.exam_id}"

class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    scores = models.JSONField()         # This will store subject-wise scores
    quiz_results = models.JSONField(default=dict)   # This will store the exam paper data

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"Result for {self.student.name} in {self.exam.exam_id}"
