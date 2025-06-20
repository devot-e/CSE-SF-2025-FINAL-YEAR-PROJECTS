from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from results.models import Exam, Result, Student, Teacher
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from django.db.models import Avg, Count
from exam_conduct.utility import is_teacher,is_student
from exam_conduct.utility import create_radar_chart,process_quiz_data

# Helper function to generate plot images
def generate_plot():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

@user_passes_test(is_teacher)
def exam_analysis_detail(request, exam_id):
    exam = get_object_or_404(Exam, exam_id=exam_id)
    results = Result.objects.filter(exam=exam)

    scores = []
    result_count=0
    avg_score = 0
    for result in results:
        result_count+=1
        scores.append(result.quiz_results['percentage'])
        avg_score+=result.quiz_results['percentage']
    # Overall exam statistics
    avg_score /=result_count
    participation_count = results.count()

    # Score distribution plot
    plt.figure(figsize=(10, 5))
    plt.hist(scores, bins=10, edgecolor='black', color='#4e73df')
    plt.title(f'Score Distribution for {exam.exam_id}')
    plt.xlabel('Scores')
    plt.ylabel('Number of Students')
    score_plot = generate_plot()
    plt.close()

    # Question analysis
    question_stats = []
    for idx in range(len(exam.quiz_questions)):
        correct = sum(1 for result in results
                     if result.quiz_results['results'][idx]['is_correct'])
        total = results.count()
        question_stats.append({
            'number': idx,
            'text': exam.quiz_questions[idx]['question'],
            'correct': correct,
            'total': total,
            'percentage': round((correct/total)*100, 2) if total > 0 else 0
        })

    context = {
        'exam': exam,
        'results':results,
        'avg_score': round(avg_score, 2) if avg_score else 0,
        'participation_count': participation_count,
        'score_plot': score_plot,
        'question_stats': question_stats,
    }
    return render(request, 'ExamAnalysis/exam_analysis.html', context)

@login_required
def result_analysis_detail(request, exam_id, student_id):
    exam = get_object_or_404(Exam, exam_id=exam_id)
    student = get_object_or_404(Student, student_id=student_id)
    result = get_object_or_404(Result, exam=exam, student=student)

    # Student's performance vs class average
    class_results = Result.objects.filter(exam=exam)
    result_count=0
    avg_score = 0
    for tresult in class_results:
        result_count+=1
        avg_score+=tresult.quiz_results['percentage']
    avg_score /=result_count

    # Comparison plot
    plt.figure(figsize=(8, 4))
    bars = plt.bar(['Your Score', 'Class Average'],
                  [result.quiz_results['percentage'], avg_score],
                  color=['#1cc88a', '#36b9cc'])
    plt.bar_label(bars, fmt='%.1f%%')
    plt.title('Your Performance vs Class Average')
    plt.ylim(0, 100)
    comparison_plot = generate_plot()
    plt.close()

    # Question-wise analysis
    question_analysis = result.quiz_results['results']
    ''' each elements format
        {'topic': 'questions/CN.json',
        'question': 'What is the maximum length of a MAC address?',
        'is_correct': False,
        'user_answer': ' 128 bits',
        'correct_answer': ' 48 bits'
        }
    '''
    # for question in exam.quiz_questions:
    #     student_answer = result.quiz_results['answers'].get(str(question['questionNo']))
    #     is_correct = student_answer == question['correctoption']
    #     question_analysis.append({
    #         'question': question['question'],
    #         'your_answer': student_answer,
    #         'correct_answer': question['correctoption'],
    #         'is_correct': is_correct
    #     })

    context = {
        'exam': exam,
        'student': student,
        'result': result,
        'comparison_plot': comparison_plot,
        'question_analysis': question_analysis,
        'class_avg': round(avg_score, 2) if avg_score else 0,
        'radar_plot': create_radar_chart(*process_quiz_data(result.quiz_results['results']))
    }
    return render(request, 'ExamAnalysis/result_analysis.html', context)

@login_required
def student_performance(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    results = Result.objects.filter(student=student).order_by('date')

    # Performance trend plot
    dates = [result.date.strftime('%Y-%m-%d') for result in results]
    scores = [result.quiz_results['percentage'] for result in results]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, scores, marker='o', color='#4e73df', linestyle='-')
    plt.axhline(y=np.mean(scores), color='r', linestyle='--', label='Average')
    plt.title('Your Performance Over Time')
    plt.xlabel('Exam Date')
    plt.ylabel('Score (%)')
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.legend()
    performance_plot = generate_plot()
    plt.close()

    # Subject-wise performance
    subject_stats = []
    subjects = set()
    for result in results:
        for subject, score in result.scores.items():
            if subject != 'total':
                subjects.add(subject)

    for subject in subjects:
        subject_scores = [r.scores.get(subject, 0) for r in results if subject in r.scores]
        if subject_scores:
            subject_stats.append({
                'subject': subject,
                'average': round(np.mean(subject_scores), 2),
                'highest': max(subject_scores),
                'lowest': min(subject_scores)
            })

    context = {
        'student': student,
        'results': results,
        'performance_plot': performance_plot,
        'subject_stats': subject_stats,
        'overall_avg': round(np.mean(scores), 2) if scores else 0,
    }
    return render(request, 'ExamAnalysis/student_performance.html', context)
