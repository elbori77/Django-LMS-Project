from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, UserAttempt
from django.contrib.auth.decorators import login_required
from .forms import StyledUserCreationForm, StyledAuthenticationForm, StyledPasswordResetForm, StyledSetPasswordForm
from django.urls import reverse_lazy
from datetime import datetime
from django.utils import timezone
import random
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

def home_view(request):
    return render(request, 'exams/home.html')

def signup_view(request):
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StyledUserCreationForm()
    return render(request, 'exams/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StyledAuthenticationForm()
    return render(request, 'exams/login.html', {'form': form}) 

@login_required
def dashboard_view(request):
    return render(request, 'exams/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'exams/exam_list.html', {'exams': exams})

@login_required
def take_exam(request, exam_id):
    
    exam = get_object_or_404(Exam, id=exam_id)
     
    # ✅ Session key for this exam
    exam_key = f'exam_{exam_id}_questions'

    # ✅ Load existing question IDs from session if present
    question_ids = request.session.get(exam_key)
    if question_ids:
        questions = list(Question.objects.filter(id__in=question_ids))
        # Ensure original order (Django doesn't preserve list order)
        questions.sort(key=lambda q: question_ids.index(q.id))
    else:
        questions = list(Question.objects.filter(exam=exam))
        random.shuffle(questions)
        questions = questions[:90]
        # ✅ Save to session
        request.session[exam_key] = [q.id for q in questions]
        request.session['exam_start_time'] = timezone.now().isoformat()

    if request.method == 'POST':
        correct_answers = 0
        feedback = {}

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')
            if question.question_type == 'multiple_choice':
                if user_answer == question.correct_option:
                    correct_answers += 1
                else:
                    feedback[question.text] = {
                        'your_answer': user_answer,
                        'correct_answer': question.correct_option
                    }
            else:
                feedback[question.text] = {
                    'your_answer': user_answer,
                    'correct_answer': '[manual grading required]'
                }

        percent = (correct_answers / len(questions)) * 100
        scaled_score = int((percent / 100) * 800 + 100)
        passed = scaled_score >= 750

        start_time = parse_datetime(request.session.get('exam_start_time'))
        end_time = timezone.now()
        time_taken = end_time - start_time

        UserAttempt.objects.create(
            user=request.user,
            exam=exam,
            score=scaled_score,
            time_taken=time_taken,
            feedback=feedback
        )

        # ✅ Clean up session
        request.session.pop(exam_key, None)
        request.session.pop('exam_start_time', None)

        return render(request, 'exams/results.html', {
            'exam': exam,
            'score': scaled_score,
            'passed': passed,
            'feedback': feedback,
            'time_taken': time_taken
        })

    exam_start_time_str = request.session.get('exam_start_time')
    if exam_start_time_str:
        exam_start_time = parse_datetime(exam_start_time_str)
        remaining_seconds = 90 * 60 - int((timezone.now() - exam_start_time).total_seconds())
        remaining_seconds = max(remaining_seconds, 0)
    else:
        remaining_seconds = 90 * 60
    return render(request, 'exams/take_exam.html', {
    'exam': exam,
    'questions': questions,
    'remaining_seconds': remaining_seconds,
    'start_time': now().isoformat(),
    
})
        
    

def exam_results(request):
    attempts = UserAttempt.objects.filter(user=request.user)
    return render(request, 'exams/results.html', {'attempts': attempts})

#Scoreboard View
@login_required
def scoreboard_view(request):
    return render(request, 'exams/scoreboard.html', {
        'a_attempts': request.user.userattempt_set.filter(exam__name__icontains='A+').order_by('-timestamp'),
        'net_attempts': request.user.userattempt_set.filter(exam__name__icontains='Network+').order_by('-timestamp'),
        'sec_attempts': request.user.userattempt_set.filter(exam__name__icontains='Security+').order_by('-timestamp'),
    })



# Custom Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    form_class = StyledPasswordResetForm
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'