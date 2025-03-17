from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, UserAttempt
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import StyledUserCreationForm, StyledAuthenticationForm

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

def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)
    
    if request.method == 'POST':
        correct_answers = 0
        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            if selected_answer == question.correct_option:
                correct_answers += 1
        
        score = (correct_answers / questions.count()) * 100
        UserAttempt.objects.create(user=request.user, exam=exam, score=score)
        return redirect('exam_list')

    return render(request, 'exams/take_exam.html', {'exam': exam, 'questions': questions})

def exam_results(request):
    attempts = UserAttempt.objects.filter(user=request.user)
    return render(request, 'exams/results.html', {'attempts': attempts})

