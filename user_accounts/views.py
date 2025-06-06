from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import (
    CustomLoginForm, CustomPasswordResetForm, CustomSetPasswordForm,
    AddTeacherForm, AddStudentForm, BulkUploadForm
)
from results.models import Teacher, Student
import pandas as pd

def is_admin(user):
    return user.is_superuser

def is_teacher(user):
    return Teacher.objects.filter(user=user).exists()

def is_student(user):
    return Student.objects.filter(user=user).exists()

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'user_accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('admin_dashboard')
        elif Teacher.objects.filter(user=user).exists():
            return reverse_lazy('teacher_dashboard')
        elif Student.objects.filter(user=user).exists():
            return reverse_lazy('student_dashboard')
        return reverse_lazy('home')

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'user_accounts/password_reset.html'
    email_template_name = 'user_accounts/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'user_accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user_accounts/password_reset_done.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'user_accounts/password_reset_complete.html'

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    teachers = Teacher.objects.all()
    students = Student.objects.all()
    return render(request, 'user_accounts/admin_dashboard.html', {
        'teachers': teachers,
        'students': students
    })

@login_required
@user_passes_test(is_admin)
def add_teacher(request):
    if request.method == 'POST':
        form = AddTeacherForm(request.POST)
        if form.is_valid():
            # Create User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # Create Teacher
            teacher = form.save(commit=False)
            teacher.user = user
            teacher.save()
            messages.success(request, 'Teacher added successfully!')
            return redirect('admin_dashboard')
    else:
        form = AddTeacherForm()
    return render(request, 'user_accounts/add_teacher.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def add_student(request):
    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            # Create User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # Create Student
            student = form.save(commit=False)
            student.user = user
            student.save()
            messages.success(request, 'Student added successfully!')
            return redirect('admin_dashboard')
    else:
        form = AddStudentForm()
    return render(request, 'user_accounts/add_student.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def bulk_upload(request):
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            user_type = form.cleaned_data['user_type']
            try:
                # Read the Excel file
                df = pd.read_excel(file)
                success_count = 0
                error_count = 0

                for _, row in df.iterrows():
                    try:
                        print(row)
                        # Create User
                        user = User.objects.create_user(
                            username=row['username'],
                            email=row['email'],
                            password=row['password']
                        )

                        if user_type == 'teacher':
                            Teacher.objects.create(
                                user=user,
                                name=row['name'],
                                # teacher_id=row['teacher_id'],
                                email=row['email'],
                                phone=row['phone']
                            ).save()
                        else:
                            Student.objects.create(
                                user=user,
                                name=row['name'],
                                # student_id=row['student_id'],
                                email=row['email'],
                                phone=row['phone']
                            ).save()
                        success_count += 1
                    except Exception as e:
                        print(e)
                        error_count += 1
                        continue

                messages.success(request, f'Successfully added {success_count} users. Failed: {error_count}')
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')

            return redirect('admin_dashboard')
    else:
        form = BulkUploadForm()

    return render(request, 'user_accounts/bulk_upload.html', {'form': form})

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    return render(request, 'user_accounts/student_dashboard.html', context)

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    teacher = Teacher.objects.get(user=request.user)
    context = {
        'teacher': teacher,
    }
    return render(request, 'user_accounts/teacher_dashboard.html', context)

@login_required
@user_passes_test(lambda u: is_teacher(u)|is_student(u))
def dashboard(request):
    if is_teacher(request.user):
        teacher = Teacher.objects.get(user=request.user)
        context = {
            'teacher': teacher,
        }
        return render(request, 'user_accounts/teacher_dashboard.html', context)
    elif is_student(request.user):
        student = Student.objects.get(user=request.user)
        context = {
            'student': student,
        }
        return render(request, 'user_accounts/student_dashboard.html', context)
    elif is_admin(request.user):
        admin = Admin.objects.get(user=request.user)
        context = {
            'admin': admin,
        }
        return render(request, 'user_accounts/admin_dashboard.html', context)
    elif is_super_admin(request.user):
        super_admin = SuperAdmin.objects.get(user=request.user)
        context = {
            'super_admin': super_admin,
        }
        return render(request, 'user_accounts/super_admin_dashboard.html', context)
