"""
Views for Attendance Management System
"""
import json
import base64
import logging
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, F
from django.utils import timezone
from django.core.paginator import Paginator
from .models import (User, Student, Teacher, ClassSession, AttendanceRecord, 
                     FaceData, ClassLog, SystemSettings)
from .forms import (StudentRegistrationForm, TeacherRegistrationForm, UserLoginForm,
                   FaceRegistrationForm, CreateClassSessionForm, MarkAttendanceForm,
                   AttendanceFilterForm)
from .face_recognition_utils import face_manager

logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def index(request):
    """Home page - always shows home page first"""
    return render(request, 'attendance/index.html')


def student_register(request):
    """Student registration view"""
    # Allow users to view and register (logout option available)
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.user_type = 'student'
            user.save()
            
            # Create Student profile
            Student.objects.create(
                user=user,
                roll_number=form.cleaned_data.get('roll_number'),
                class_name=form.cleaned_data.get('class_name')
            )
            
            # Register face if provided
            face_image = request.FILES.get('face_image')
            if face_image:
                try:
                    success, msg, _ = face_manager.register_face(user, face_image)
                    if success:
                        messages.success(request, 'Face registered successfully! Please login.')
                    else:
                        messages.warning(request, f'Face registration failed: {msg}. But your account is created. Please login.')
                except Exception as e:
                    logger.error(f"Face registration error: {str(e)}")
                    messages.warning(request, 'Face registration failed, but your account is created. You can register your face later.')
            
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Student Registration'
    }
    return render(request, 'attendance/student_register.html', context)


def teacher_register(request):
    """Teacher registration view"""
    # Allow users to view and register (logout option available)
    
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.user_type = 'teacher'
            user.save()
            
            # Create Teacher profile
            Teacher.objects.create(
                user=user,
                employee_id=form.cleaned_data.get('employee_id'),
                is_verified=False
            )
            
            messages.success(request, 'Registration successful! Please wait for admin verification.')
            return redirect('login')
    else:
        form = TeacherRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Teacher Registration'
    }
    return render(request, 'attendance/teacher_register.html', context)


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        if request.user.user_type == 'student':
            return redirect('student_dashboard')
        elif request.user.user_type == 'teacher':
            return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Get user by email
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    
                    # Set session duration
                    if form.cleaned_data.get('remember_me'):
                        request.session.set_expiry(86400 * 30)  # 30 days
                    else:
                        request.session.set_expiry(0)  # Browser close
                    
                    # Redirect based on user type
                    if user.user_type == 'student':
                        return redirect('student_dashboard')
                    elif user.user_type == 'teacher':
                        return redirect('teacher_dashboard')
                else:
                    messages.error(request, 'Invalid credentials.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login'
    }
    return render(request, 'attendance/login.html', context)


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


def register_face(request):
    """Face registration during signup"""
    if request.user.is_authenticated:
        return redirect('student_dashboard' if request.user.user_type == 'student' else 'teacher_dashboard')
    
    if request.method == 'POST':
        form = FaceRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['face_image']
            
            # For now, store this in session - user will register face after login
            request.session['face_image'] = base64.b64encode(image_file.read()).decode()
            messages.info(request, 'Face image captured. Please complete registration.')
            
            return redirect('student_register')
    else:
        form = FaceRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Face Registration'
    }
    return render(request, 'attendance/register_face.html', context)


# ============================================================================
# STUDENT VIEWS
# ============================================================================

@login_required(login_url='login')
def student_dashboard(request):
    """Student dashboard"""
    if request.user.user_type != 'student':
        return redirect('index')
    
    student = get_object_or_404(Student, user=request.user)
    
    # Get attendance statistics
    total_records = AttendanceRecord.objects.filter(student=student)
    present_count = total_records.filter(is_present=True).count()
    absent_count = total_records.filter(is_present=False).count()
    
    attendance_percentage = student.get_attendance_percentage()
    
    # Get recent attendance
    recent_attendance = AttendanceRecord.objects.filter(
        student=student
    ).select_related('class_session').order_by('-marked_at')[:10]
    
    context = {
        'student': student,
        'total_classes': total_records.count(),
        'present': present_count,
        'absent': absent_count,
        'attendance_percentage': round(attendance_percentage, 2),
        'recent_attendance': recent_attendance,
        'page_title': 'Student Dashboard'
    }
    return render(request, 'attendance/student_dashboard.html', context)


@login_required(login_url='login')
def mark_attendance(request):
    """Student marks attendance"""
    if request.user.user_type != 'student':
        return redirect('index')
    
    student = get_object_or_404(Student, user=request.user)
    
    if request.method == 'POST':
        form = MarkAttendanceForm(request.POST, request.FILES)
        if form.is_valid():
            class_key = form.cleaned_data['class_key'].upper()
            face_image = request.FILES.get('face_image')
            
            try:
                class_session = ClassSession.objects.get(class_key=class_key)
                
                # Check if class is valid for attendance
                if not class_session.is_valid_for_attendance():
                    messages.error(request, 'This class session is not active.')
                    return render(request, 'attendance/mark_attendance.html', {'form': form})
                
                # Check for duplicate attendance
                existing = AttendanceRecord.objects.filter(
                    student=student,
                    class_session=class_session
                ).first()
                
                if existing:
                    messages.warning(request, 'You have already marked attendance for this class.')
                    return render(request, 'attendance/mark_attendance.html', {'form': form})
                
                # Verify face if required
                face_verified = False
                confidence_score = 0
                
                if face_image and request.user.face_registered:
                    is_match, confidence, msg = face_manager.verify_face(request.user, face_image)
                    
                    if is_match:
                        face_verified = True
                        confidence_score = confidence
                    else:
                        messages.error(request, f'Face verification failed: {msg}')
                        return render(request, 'attendance/mark_attendance.html', {'form': form})
                
                # Create attendance record
                attendance = AttendanceRecord.objects.create(
                    student=student,
                    class_session=class_session,
                    is_present=True,
                    face_verified=face_verified,
                    verification_distance=confidence_score,
                    captured_image=face_image if face_image else None,  # Save the captured image
                    device_info=request.META.get('HTTP_USER_AGENT', '')[:200]
                )
                
                messages.success(request, f'Attendance marked successfully for {class_session.subject}!')
                return redirect('student_dashboard')
            
            except ClassSession.DoesNotExist:
                messages.error(request, 'Invalid class key.')
    else:
        form = MarkAttendanceForm()
    
    context = {
        'form': form,
        'page_title': 'Mark Attendance'
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required(login_url='login')
def attendance_history(request):
    """View attendance history"""
    if request.user.user_type != 'student':
        return redirect('index')
    
    student = get_object_or_404(Student, user=request.user)
    
    # Get filter form
    form = AttendanceFilterForm(request.GET)
    
    # Base query
    records = AttendanceRecord.objects.filter(
        student=student
    ).select_related('class_session').order_by('-marked_at')
    
    # Apply filters
    if form.is_valid():
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        class_name = form.cleaned_data.get('class_name')
        subject = form.cleaned_data.get('subject')
        
        if date_from:
            records = records.filter(marked_at__date__gte=date_from)
        if date_to:
            records = records.filter(marked_at__date__lte=date_to)
        if class_name:
            records = records.filter(class_session__class_name__icontains=class_name)
        if subject:
            records = records.filter(class_session__subject__icontains=subject)
    
    # Pagination
    paginator = Paginator(records, 20)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'page_title': 'Attendance History'
    }
    return render(request, 'attendance/attendance_history.html', context)


@login_required(login_url='login')
def upload_face(request):
    """Allow student to register/update face"""
    if request.user.user_type != 'student':
        return redirect('index')
    
    if request.method == 'POST':
        form = FaceRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['face_image']
            
            success, message, encoding = face_manager.register_face(request.user, image_file)
            
            if success:
                messages.success(request, message)
                return redirect('student_dashboard')
            else:
                messages.error(request, message)
    else:
        form = FaceRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Register Face',
        'face_registered': request.user.face_registered
    }
    return render(request, 'attendance/upload_face.html', context)


# ============================================================================
# TEACHER VIEWS
# ============================================================================

@login_required(login_url='login')
def teacher_dashboard(request):
    """Teacher dashboard"""
    if request.user.user_type != 'teacher':
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Check if verified
    if not teacher.is_verified:
        messages.warning(request, 'Your account is pending verification by administrator.')
    
    # Get statistics
    total_sessions = ClassSession.objects.filter(teacher=teacher).count()
    active_sessions = ClassSession.objects.filter(teacher=teacher, is_active=True).count()
    
    # Get today's sessions
    today = timezone.now().date()
    today_sessions = ClassSession.objects.filter(
        teacher=teacher,
        start_time__date=today
    ).order_by('start_time')
    
    # Get recent attendance
    recent_attendance = AttendanceRecord.objects.filter(
        class_session__teacher=teacher
    ).select_related('student', 'class_session').order_by('-marked_at')[:10]
    
    context = {
        'teacher': teacher,
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'today_sessions': today_sessions,
        'recent_attendance': recent_attendance,
        'page_title': 'Teacher Dashboard'
    }
    return render(request, 'attendance/teacher_dashboard.html', context)


@login_required(login_url='login')
def create_class(request):
    """Create a new class session"""
    if request.user.user_type != 'teacher':
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if request.method == 'POST':
        form = CreateClassSessionForm(request.POST)
        if form.is_valid():
            class_session = form.save(commit=False)
            class_session.teacher = teacher
            class_session.class_key = ClassSession.generate_class_key()
            class_session.duration_minutes = form.cleaned_data['duration_minutes']
            
            # Set end_time if not provided
            if not class_session.end_time:
                class_session.end_time = class_session.start_time + timedelta(
                    minutes=class_session.duration_minutes
                )
            
            class_session.save()
            
            # Log action
            ClassLog.objects.create(
                teacher=teacher,
                class_session=class_session,
                action='class_created',
                description=f'Created class session: {class_session.subject}',
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'Class created! Key: {class_session.class_key}')
            return redirect('class_detail', class_id=class_session.id)
    else:
        form = CreateClassSessionForm()
    
    context = {
        'form': form,
        'page_title': 'Create Class Session'
    }
    return render(request, 'attendance/create_class.html', context)


@login_required(login_url='login')
def class_detail(request, class_id):
    """View class session details"""
    if request.user.user_type != 'teacher':
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    class_session = get_object_or_404(ClassSession, id=class_id, teacher=teacher)
    
    # Get attendance records
    attendance_records = AttendanceRecord.objects.filter(
        class_session=class_session
    ).select_related('student').order_by('-marked_at')
    
    present_count = attendance_records.filter(is_present=True).count()
    absent_count = attendance_records.filter(is_present=False).count()
    
    context = {
        'class_session': class_session,
        'attendance_records': attendance_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'page_title': f'Class: {class_session.subject}'
    }
    return render(request, 'attendance/class_detail.html', context)


@login_required(login_url='login')
def start_class(request, class_id):
    """Start a class session"""
    if request.user.user_type != 'teacher':
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    class_session = get_object_or_404(ClassSession, id=class_id, teacher=teacher)
    
    if request.method == 'POST':
        class_session.is_active = True
        class_session.save()
        
        ClassLog.objects.create(
            teacher=teacher,
            class_session=class_session,
            action='class_started',
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, f'Class started! Key: {class_session.class_key}')
        return redirect('class_detail', class_id=class_id)
    
    return render(request, 'attendance/confirm_action.html', {
        'title': 'Start Class',
        'message': f'Are you sure you want to start "{class_session.subject}"?',
        'confirm_url': request.path
    })


@login_required(login_url='login')
def end_class(request, class_id):
    """End a class session"""
    if request.user.user_type != 'teacher':
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    class_session = get_object_or_404(ClassSession, id=class_id, teacher=teacher)
    
    if request.method == 'POST':
        class_session.is_active = False
        class_session.save()
        
        ClassLog.objects.create(
            teacher=teacher,
            class_session=class_session,
            action='class_ended',
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'Class ended. Attendance marked.')
        return redirect('teacher_dashboard')
    
    return render(request, 'attendance/confirm_action.html', {
        'title': 'End Class',
        'message': f'Are you sure you want to end "{class_session.subject}"?',
        'confirm_url': request.path
    })


@login_required(login_url='login')
def teacher_attendance_report(request):
    """View attendance report for teacher's classes"""
    if request.user.user_type != 'teacher':
        return redirect('index')
    
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Get filter form
    form = AttendanceFilterForm(request.GET)
    
    # Base query
    sessions = ClassSession.objects.filter(teacher=teacher).order_by('-start_time')
    
    # Apply filters
    if form.is_valid():
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        class_name = form.cleaned_data.get('class_name')
        subject = form.cleaned_data.get('subject')
        
        if date_from:
            sessions = sessions.filter(start_time__date__gte=date_from)
        if date_to:
            sessions = sessions.filter(start_time__date__lte=date_to)
        if class_name:
            sessions = sessions.filter(class_name__icontains=class_name)
        if subject:
            sessions = sessions.filter(subject__icontains=subject)
    
    # Add attendance statistics
    for session in sessions:
        session.present = session.get_present_count()
        session.absent = session.get_absent_count()
        session.total = session.present + session.absent
    
    # Pagination
    paginator = Paginator(sessions, 10)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'page_title': 'Attendance Report'
    }
    return render(request, 'attendance/teacher_attendance_report.html', context)


# ============================================================================
# API VIEWS (JSON RESPONSES FOR AJAX)
# ============================================================================

@login_required
@require_POST
def api_mark_attendance(request):
    """API endpoint to mark attendance with face verification"""
    try:
        data = json.loads(request.body)
        class_key = data.get('class_key', '').upper()
        face_image_data = data.get('face_image')
        
        if request.user.user_type != 'student':
            return JsonResponse({'success': False, 'message': 'Only students can mark attendance'}, status=403)
        
        student = get_object_or_404(Student, user=request.user)
        
        # Validate class key
        try:
            class_session = ClassSession.objects.get(class_key=class_key)
        except ClassSession.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid class key'}, status=400)
        
        # Check if class is active
        if not class_session.is_valid_for_attendance():
            return JsonResponse({'success': False, 'message': 'Class is not active for attendance'}, status=400)
        
        # Check for duplicate
        if AttendanceRecord.objects.filter(student=student, class_session=class_session).exists():
            return JsonResponse({'success': False, 'message': 'Attendance already marked for this class'}, status=400)
        
        face_verified = False
        confidence_score = 0
        
        # Verify face if image provided
        if face_image_data and request.user.face_registered:
            try:
                # Decode base64 image
                import io
                from django.core.files.uploadedfile import InMemoryUploadedFile
                image_data = base64.b64decode(face_image_data.split(',')[1])
                image_file = InMemoryUploadedFile(
                    io.BytesIO(image_data),
                    'ImageField',
                    'face.jpg',
                    'image/jpeg',
                    len(image_data),
                    None
                )
                
                is_match, confidence, msg = face_manager.verify_face(request.user, image_file)
                
                if is_match:
                    face_verified = True
                    confidence_score = confidence
                else:
                    return JsonResponse({'success': False, 'message': f'Face verification failed'}, status=400)
            except Exception as e:
                logger.error(f'Face verification error: {str(e)}')
                return JsonResponse({'success': False, 'message': 'Face verification error'}, status=400)
        
        # Create attendance record
        AttendanceRecord.objects.create(
            student=student,
            class_session=class_session,
            is_present=True,
            face_verified=face_verified,
            verification_distance=confidence_score,
            device_info=request.META.get('HTTP_USER_AGENT', '')[:200]
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance marked for {class_session.subject}',
            'face_verified': face_verified
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    except Exception as e:
        logger.error(f'Attendance marking error: {str(e)}')
        return JsonResponse({'success': False, 'message': 'Server error'}, status=500)


@login_required
@require_POST
def api_verify_class_key(request):
    """API endpoint to verify class key"""
    try:
        data = json.loads(request.body)
        class_key = data.get('class_key', '').upper()
        
        try:
            class_session = ClassSession.objects.get(class_key=class_key)
            
            if not class_session.is_valid_for_attendance():
                return JsonResponse({
                    'valid': False,
                    'message': 'Class session not active'
                })
            
            return JsonResponse({
                'valid': True,
                'class_name': class_session.class_name,
                'subject': class_session.subject,
                'end_time': class_session.end_time.isoformat()
            })
        except ClassSession.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'message': 'Invalid class key'
            })
    
    except json.JSONDecodeError:
        return JsonResponse({'valid': False, 'message': 'Invalid request'}, status=400)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
