from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, UserAttempt, UserSettings
from django.contrib.auth.decorators import login_required
from .forms import StyledUserCreationForm, StyledAuthenticationForm, StyledPasswordResetForm, StyledSetPasswordForm, StyledPasswordChangeForm
from django.urls import reverse_lazy
from datetime import datetime
from django.utils import timezone
import random, json
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.contrib import messages


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
    settings = UserSettings.objects.get(user=request.user)
    use_timer = settings.timer_enabled
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        # Get selected questions from POST
        question_ids_str = request.POST.get("question_ids", "")
        question_ids = [int(qid) for qid in question_ids_str.split(",") if qid.strip().isdigit()]
        selected_questions = list(Question.objects.filter(id__in=question_ids))
    else:
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
                    user_answer_text = (
                        f"{user_answer}: {getattr(q, f'option_{user_answer.lower()}', '')}"
                        if user_answer else "No answer"
                    )
                    correct_text = f"{correct_letter}: {getattr(q, f'option_{correct_letter.lower()}', '')}"
                    feedback[q.text] = {
                        'your_answer': user_answer_text,
                        'correct_answer': correct_text
                    }

            elif q.question_type == 'drag_and_drop':
                extra_data = q.extra_data or {}
                correct_pairs = extra_data.get("pairs", {})
                user_response = user_answer or ""

                user_pairs = dict(
                    pair.split("->") for pair in user_response.strip(",").split(",") if "->" in pair
                )

                total_pairs = len(correct_pairs)
                correct_count = sum(1 for k, v in correct_pairs.items() if user_pairs.get(k) == v)

                if total_pairs > 0 and correct_count == total_pairs:
                    correct += 1
                else:
                    feedback[q.text] = {
                        'your_answer': user_pairs or "No answer",
                        'correct_answer': correct_pairs
                    }


        scaled_score = round(100 + ((correct / 90) * 800))
        passed = scaled_score >= 720
        start_dt = timezone.datetime.fromisoformat(start_time)
        time_taken = timezone.now() - start_dt
        time_taken_str = str(time_taken).split('.')[0]

        UserAttempt.objects.create(
            user=request.user,
            exam=exam,
            score=scaled_score,
            time_taken=time_taken,
            feedback=feedback
        )

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
        'start_time': timezone.now().isoformat(),
        'use_timer': use_timer,
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
def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@login_required
def scoreboard_view(request):
    a_attempts = request.user.userattempt_set.filter(exam__name__icontains='A+').order_by('-timestamp')
    net_attempts = request.user.userattempt_set.filter(exam__name__icontains='Network+').order_by('-timestamp')
    sec_attempts = request.user.userattempt_set.filter(exam__name__icontains='Security+').order_by('-timestamp')

    # Add formatted_time to each attempt
    for attempt_list in [a_attempts, net_attempts, sec_attempts]:
        for attempt in attempt_list:
            attempt.formatted_time = format_timedelta(attempt.time_taken)

    return render(request, 'exams/scoreboard.html', {
        'a_attempts': a_attempts,
        'net_attempts': net_attempts,
        'sec_attempts': sec_attempts,
    })



@login_required
def settings_view(request):
    settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings.timer_enabled = request.POST.get('timer_enabled') == 'on'
        settings.save()
        messages.success(request, 'Settings updated successfully.')
        return redirect('settings')

    return render(request, 'exams/settings.html', {'settings': settings})


@login_required
def reset_scoreboard(request):
    if request.method == 'POST':
        request.user.userattempt_set.all().delete()
        messages.success(request, 'Scoreboard reset successfully.')
        return redirect('settings')
    return render(request, 'exams/reset_scoreboard_confirm.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('settings')
    else:
        form = StyledPasswordChangeForm(user=request.user)

    return render(request, 'exams/change_password.html', {'form': form})



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