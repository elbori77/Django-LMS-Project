from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, UserAttempt
from django.contrib.auth.decorators import login_required
from .forms import StyledUserCreationForm, StyledAuthenticationForm, StyledPasswordResetForm, StyledSetPasswordForm
from django.urls import reverse_lazy
from datetime import datetime
from django.utils import timezone
import random, json
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
    questions = list(Question.objects.filter(exam=exam))
    random.shuffle(questions)
    selected_questions = questions[:90]

    if request.method == 'POST':
        answers = json.loads(request.POST.get('answers', '{}'))
        start_time = request.POST.get('start_time')
        correct = 0
        feedback = {}

        for q in selected_questions:
            qid = str(q.id)
            user_answer = answers.get(qid)

            correct_letter = q.correct_option or ''
            correct_text = getattr(q, f'option_{correct_letter.lower()}', '') if correct_letter else ''

            if q.question_type in ['multiple_choice', 'true_false']:
                if user_answer == correct_letter:
                    correct += 1
                else:
                    feedback[q.text] = {
                        'your_answer': user_answer or "No answer",
                        'correct_answer': f"{correct_letter}: {correct_text}"
                    }

            elif q.question_type == 'drag_and_drop':
                pass  # DnD grading if needed
    

        # CompTIA scaled score (100–900)
        scaled_score = round(100 + ((correct / 90) * 800))
        passed = scaled_score >= 720

        # Parse time
        start_dt = timezone.datetime.fromisoformat(start_time)
        time_taken = timezone.now() - start_dt
        time_taken_str = str(time_taken).split('.')[0]  # removes microseconds

        


        # Save attempt
        UserAttempt.objects.create(
            user=request.user,
            exam=exam,
            score=scaled_score,
            time_taken=time_taken,
            feedback=feedback
        )

        # Show result page immediately
        return render(request, 'exams/exam_results.html', {
            'exam': exam,
            'score': scaled_score,
            'time_taken': time_taken_str,
            'passed': passed,
            'feedback': feedback,
            'timestamp': timezone.now(),
        })

    return render(request, 'exams/take_exam.html', {
        'exam': exam,
        'questions': selected_questions,
        'start_time': timezone.now().isoformat()
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
    return render(request, 'exams/exam_results.html', {'attempts': attempts})

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