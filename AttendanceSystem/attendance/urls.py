"""
URL routing for Attendance Management System
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('student-register/', views.student_register, name='student_register'),
    path('teacher-register/', views.teacher_register, name='teacher_register'),
    path('register-face/', views.register_face, name='register_face'),
    
    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('student/attendance-history/', views.attendance_history, name='attendance_history'),
    path('student/upload-face/', views.upload_face, name='upload_face'),
    
    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/create-class/', views.create_class, name='create_class'),
    path('teacher/class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('teacher/class/<int:class_id>/start/', views.start_class, name='start_class'),
    path('teacher/class/<int:class_id>/end/', views.end_class, name='end_class'),
    path('teacher/attendance-report/', views.teacher_attendance_report, name='teacher_attendance_report'),
    
    # API endpoints
    path('api/mark-attendance/', views.api_mark_attendance, name='api_mark_attendance'),
    path('api/verify-class-key/', views.api_verify_class_key, name='api_verify_class_key'),
]
