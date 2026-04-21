"""
Models for Attendance Management System
"""
import os
import uuid
import secrets
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    face_encoding = models.TextField(blank=True, null=True)  # Stores face encoding as JSON
    face_registered = models.BooleanField(default=False)
    face_image_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active_user = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"


class Student(models.Model):
    """Student profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9]+$', 'Roll number must contain only letters and numbers')]
    )
    class_name = models.CharField(max_length=50)  # e.g., "10-A", "12-B"
    enrollment_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    total_classes_attended = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('roll_number',)
        ordering = ['roll_number']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"
    
    def get_attendance_percentage(self, subject=None):
        """Calculate attendance percentage"""
        records = AttendanceRecord.objects.filter(student=self)
        if subject:
            records = records.filter(class_session__subject=subject)
        
        if not records.exists():
            return 0
        
        attended = records.filter(is_present=True).count()
        total = records.count()
        return (attended / total) * 100 if total > 0 else 0


class Teacher(models.Model):
    """Teacher profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    verification_code = models.CharField(max_length=10, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        ordering = ['employee_id']
    
    def __str__(self):
        return f"Prof. {self.user.get_full_name()}"
    
    def get_active_classes(self):
        """Get all active class sessions for this teacher"""
        now = timezone.now()
        return ClassSession.objects.filter(
            teacher=self,
            start_time__lte=now,
            end_time__gte=now,
            is_active=True
        )


class ClassSession(models.Model):
    """Class session model - represents a single class"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='class_sessions')
    subject = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)  # e.g., "10-A", "12-B"
    class_key = models.CharField(max_length=10, unique=True)  # Unique code for attendance
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_students = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Class Session'
        verbose_name_plural = 'Class Sessions'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['class_key']),
            models.Index(fields=['teacher', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.class_name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    @staticmethod
    def generate_class_key():
        """Generate a unique 6-character class key"""
        return secrets.token_hex(3).upper()[:6]
    
    def is_valid_for_attendance(self):
        """Check if class is currently valid for marking attendance"""
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time
    
    def get_attendance_records(self):
        """Get all attendance records for this class"""
        return self.attendance_records.all()
    
    def get_present_count(self):
        """Get count of students marked present"""
        return self.attendance_records.filter(is_present=True).count()
    
    def get_absent_count(self):
        """Get count of students marked absent"""
        return self.attendance_records.filter(is_present=False).count()


class AttendanceRecord(models.Model):
    """Attendance record model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='attendance_records')
    is_present = models.BooleanField(default=False)
    marked_at = models.DateTimeField(auto_now_add=True)
    face_verified = models.BooleanField(default=False)
    verification_distance = models.FloatField(null=True, blank=True)  # Face match distance
    captured_image = models.ImageField(upload_to='attendance_captures/%Y/%m/%d/', null=True, blank=True)  # Live captured photo
    location = models.CharField(max_length=100, blank=True)
    device_info = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        unique_together = ('student', 'class_session')
        ordering = ['-marked_at']
        indexes = [
            models.Index(fields=['student', 'class_session']),
            models.Index(fields=['marked_at']),
        ]
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.roll_number} - {self.class_session.subject} - {status}"


class FaceData(models.Model):
    """Store face encodings for security"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='face_data')
    face_encoding = models.TextField()  # JSON array of face encoding
    image_path = models.ImageField(upload_to='face_images/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)
    quality_score = models.FloatField(default=0)  # Quality of face (0-1)
    
    class Meta:
        verbose_name = 'Face Data'
        verbose_name_plural = 'Face Data'
    
    def __str__(self):
        return f"Face data for {self.user}"


class ClassLog(models.Model):
    """Log model to track teacher actions"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='class_logs')
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, blank=True, null=True)
    action = models.CharField(max_length=100)  # e.g., 'class_started', 'class_ended', 'key_generated'
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Class Log'
        verbose_name_plural = 'Class Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['teacher', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.teacher} - {self.action} ({self.timestamp})"


class SystemSettings(models.Model):
    """System-wide settings"""
    class_key_validity_hours = models.IntegerField(default=8)
    face_recognition_threshold = models.FloatField(default=0.6)
    max_daily_attempts = models.IntegerField(default=5)
    require_face_verification = models.BooleanField(default=True)
    enable_duplicate_detection = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return "System Configuration"
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
