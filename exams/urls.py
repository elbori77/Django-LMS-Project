from django.urls import path
from .views import signup_view, login_view, logout_view, exam_list, take_exam, exam_results, home_view, dashboard_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('exams/', exam_list, name='exam_list'),
    path('exams/<int:exam_id>/', take_exam, name='take_exam'),
    path('results/', exam_results, name='exam_results'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]
