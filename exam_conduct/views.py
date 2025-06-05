from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from results.models import Exam, Result, Student
from .models import ExamSession
from .forms import ExamAccessForm
import json
from django.utils import timezone
from .utility import generate_quiz_report
def exam_entry(request):
    if request.method == 'POST':
        form = ExamAccessForm(request.POST)
        if form.is_valid():
            exam_id = form.cleaned_data['exam_id']
            try:
                exam = Exam.objects.get(exam_id=exam_id)
                if not request.user.is_authenticated or not hasattr(request.user, 'student'):
                    return redirect('login')

                student = request.user.student
                # Check if student already took this exam
                if Result.objects.filter(exam=exam, student=student).exists():
                    return render(request, 'exam_conduct/exam_taken.html')

                # Create new exam session
                session = ExamSession.objects.create(exam=exam, student=student)
                return redirect('exam_conduct:exam_interface', session_id=session.session_id)

            except Exam.DoesNotExist:
                form.add_error('exam_id', 'Invalid Exam ID')
    else:
        form = ExamAccessForm()

    return render(request, 'exam_conduct/exam_entry.html', {'form': form})

def exam_interface(request, session_id):
    session = get_object_or_404(ExamSession, session_id=session_id, student=request.user.student)
    exam = session.exam
    questions = exam.quiz_questions

    context = {
        'exam': exam,
        'questions': questions,
        'session_id': session_id,
        # 'duration': exam.quiz_questions.get('duration', 60),  # in minutes
        'duration': len(exam.quiz_questions)*2,  # in minutes
    }
    return render(request, 'exam_conduct/exam_interface.html', context)

'''
@csrf_exempt
def submit_exam(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(ExamSession, session_id=session_id, student=request.user.student)
        exam = session.exam

        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
            print(answers,'--------------')
            # Calculate score (implement your own scoring logic)
            score = calculate_score(exam.quiz_questions, answers)

            # Save result
            Result.objects.create(
                exam=exam,
                student=request.user.student,
                teacher=exam.teacher,
                scores={'total': score},
                quiz_results={
                    'answers': answers,
                    'session_data': {
                        'warnings': session.warnings,
                        'fullscreen_exits': session.fullscreen_exits,
                        'tab_switches': session.tab_switches
                    }
                }
            )

            # End session
            session.is_active = False
            session.end_time = timezone.now()
            session.save()

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
'''

@csrf_exempt
def submit_exam(request,session_id):
    if request.method == 'POST':
        # Get the original quiz data
        session = get_object_or_404(ExamSession, session_id=session_id, student=request.user.student)
        quiz_data = session.exam.quiz_questions;
        # Check if quiz_data is empty
        if not quiz_data:
            return HttpResponse("<h1>No quiz data found.</h1>")

        score = 0
        results = []
        q_num=1
        for question in quiz_data:
            # q_num = question['questionNo']
            user_answer = request.POST.get(f'q{q_num}')
            is_correct = (user_answer == question['correctoption'])

            if is_correct:
                score += 1

            results.append({
                'question': question['question'],
                'user_answer': " " + quiz_data[q_num-1]['option' + user_answer] if user_answer else "NOT ANSWERED",
                'correct_answer': " " + quiz_data[q_num-1]['option' + question['correctoption']],
                'is_correct': is_correct,
                'topic': question['topic']
            })
            q_num+=1

        # Calculate percentage
        percentage = (score / len(quiz_data)) * 100

        # Generate report using the utility functions
        report = generate_quiz_report(results)

        # Prepare context with both raw results and processed report
        context = {
            'results': results,
            'score': score,
            'total': len(quiz_data),
            'percentage': percentage,

            # 'quiz_data': quiz_data,
            'topics': report['topics'],
            'accuracy': report['accuracy'],
            'radar_chart': report['chart_image'],
            # 'score': f"{report['correct_answers']}/{report['total_questions']}",
            # 'percentage': (report['correct_answers'] / report['total_questions']) * 100,
        }

        Result.objects.create(
            exam = session.exam,
            student = session.student,
            teacher = session.exam.teacher,
            date = timezone.now().date(),
            scores = dict(zip(context['topics'],context['accuracy'])),
            quiz_results = context
        )
        return render(request, 'quiz_results.html', context)

    return redirect('quiz')


def calculate_score(quiz_data, answers):
    # Implement your scoring logic here
    total_questions = len(quiz_data.get('questions', []))
    correct_answers = 0

    for question in quiz_data.get('questions', []):
        q_id = str(question['id'])
        if q_id in answers and answers[q_id] == question['correct_answer']:
            correct_answers += 1

    return round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0

@csrf_exempt
def proctoring_alert(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(ExamSession, session_id=session_id)
        data = json.loads(request.body)
        violation_type = data.get('type')

        if violation_type == 'fullscreen_exit':
            session.fullscreen_exits += 1
        elif violation_type == 'tab_switch':
            session.tab_switches += 1
        elif violation_type == 'warning':
            session.warnings += 1

        session.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)
