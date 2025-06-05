from django.shortcuts import render ,redirect
from django.conf import settings
import os
import random
import json
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from .utility import generate_quiz_report ,is_teacher,is_student
from django.contrib.auth.decorators import login_required, user_passes_test
from results.models import Teacher,Student,Result,Exam
from django.http import HttpResponse,HttpResponseNotFound
from django.utils import timezone
# Create your views here.

@csrf_exempt
@login_required
@user_passes_test(is_teacher)
def genQ(request):
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Headers: {request.headers}")
    print(f"User: {request.user}")
    if request.method == 'POST':
        # Process form submission
        values = []
        total = 0
        # Get all five values from the form
        for i in range(1, 6):
            field_name = f'value{i}'
            value = int(request.POST.get(field_name, 0))
            values.append(value)
            total += value
        # print(values)
        index_of_questions = []
        x=["CN","DBMS","DSA","OS","TOC"]
        for i in range(5):
            x[i]="questions/"+x[i]+".json"
            # x[i]=os.path.join(settings.BASE_DIR,x[i])
            # print(os.path.join(settings.BASE_DIR,x[i]))
        for i in range(5):
            index_of_questions.append(random.sample(range(100), values[i]))
        list_of_questions = []
        for i in range(5):
            file_path = os.path.join(settings.BASE_DIR, x[i])
            with open(file_path) as f:
                data = json.load(f)
            for j in index_of_questions[i]:
                # print(data[j])
                dict = data[j]
                dict['topic']=x[i]
                list_of_questions.append(dict)
        # print(list_of_questions)
        # You can now use these values as needed
        # For example: save to database, perform calculations, etc.

        # Return the same template with the submitted values preserved
        # request.session.clear()
        request.session['quiz_data'] = list_of_questions
        # request.session['total'] = total
        print(list_of_questions)
        return render(request, 'quiz_template.html', {'quiz_data': list_of_questions, 'total': total})

    # GET request - just show the empty form
    return render(request, 'genQ.html')

@csrf_exempt
@login_required
@user_passes_test(is_teacher)
def save_quiz(request):
    if request.method == 'POST':
        # Get the original quiz data
        quiz_data = request.session.get('quiz_data', [])
        # Check if quiz_data is empty
        if not quiz_data:
            return HttpResponse("<h1>No quiz data found.</h1>")

        # Save the quiz data to the database or perform other actions
        # For example: save to database, perform calculations, etc.
        examiner=Teacher.objects.get(user=request.user)
        now = timezone.now()
        exam_id = f"EXAM{now.strftime('%Y%m%d%H%M%S')}"

        # Save to the Exam model
        exam = Exam.objects.create(
            exam_id=exam_id,
            teacher=examiner,
            quiz_questions=quiz_data
        )

        return render(request, 'examCreatedSuccess.html', {'exam_id': exam_id})

@login_required
@user_passes_test(is_teacher)
def delete_exam(request, exam_id):
    try:
        exam = Exam.objects.get(exam_id=exam_id)
        exam.delete()
        return redirect('dashboard')
    except Exam.DoesNotExist:
        return HttpResponse("<h1>No exam data found.</h1>")

@csrf_exempt
@login_required
@user_passes_test(is_student)
def submit_quiz(request):
    if request.method == 'POST':
        # Get the original quiz data
        quiz_data = request.session.get('quiz_data', [])
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

        return render(request, 'quiz_results.html', context)

    return redirect('quiz')
