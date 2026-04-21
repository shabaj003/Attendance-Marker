"""
Admin configuration for Attendance Management System
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import (User, Student, Teacher, ClassSession, AttendanceRecord,
                     FaceData, ClassLog, SystemSettings)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Custom admin for User model"""
    list_display = ('get_full_name', 'email', 'user_type', 'phone', 'face_registered', 'created_at')
    list_filter = ('user_type', 'face_registered', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'face_registered')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Account Type', {
            'fields': ('user_type', 'is_active_user')
        }),
        ('Face Recognition', {
            'fields': ('face_registered', 'face_image_path'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Name'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user_type',)
        return self.readonly_fields


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Custom admin for Student model"""
    list_display = ('roll_number', 'get_student_name', 'class_name', 'enrollment_date', 'is_verified', 'get_attendance_badge')
    list_filter = ('class_name', 'is_verified', 'enrollment_date')
    search_fields = ('roll_number', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('enrollment_date', 'total_classes_attended')
    actions = ['delete_selected_students']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'roll_number', 'class_name')
        }),
        ('Status', {
            'fields': ('is_verified',)
        }),
        ('Statistics', {
            'fields': ('enrollment_date', 'total_classes_attended'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_name(self, obj):
        return obj.user.get_full_name()
    get_student_name.short_description = 'Student Name'
    
    def get_attendance_badge(self, obj):
        percentage = obj.get_attendance_percentage()
        if percentage >= 80:
            color = 'green'
        elif percentage >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            f'{percentage:.1f}%'
        )
    get_attendance_badge.short_description = 'Attendance %'
    
    def delete_selected_students(self, request, queryset):
        """Custom delete action with confirmation"""
        count = queryset.count()
        deleted_count = 0
        for student in queryset:
            try:
                # Delete the associated user too
                user = student.user
                student.delete()
                user.delete()
                deleted_count += 1
            except Exception as e:
                self.message_user(request, f'Error deleting {student.roll_number}: {str(e)}', level='error')
        
        self.message_user(request, f'Successfully deleted {deleted_count} student(s) and their accounts.')
    delete_selected_students.short_description = 'Delete selected students and their accounts'
    
    def has_delete_permission(self, request, obj=None):
        """Only superuser can delete"""
        return request.user.is_superuser


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Custom admin for Teacher model"""
    list_display = ('get_teacher_name', 'employee_id', 'department', 'subject', 'is_verified', 'get_classes_count')
    list_filter = ('department', 'is_verified', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'subject')
    readonly_fields = ('created_at', 'verification_code')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Professional Details', {
            'fields': ('department', 'subject')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_code')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_teachers', 'unverify_teachers', 'delete_selected_teachers']
    
    def get_teacher_name(self, obj):
        return f"Prof. {obj.user.get_full_name()}"
    get_teacher_name.short_description = 'Teacher Name'
    
    def get_classes_count(self, obj):
        count = obj.class_sessions.count()
        return format_html(
            '<span style="background-color: #e7f3ff; padding: 2px 8px; border-radius: 3px;">{}</span>',
            count
        )
    get_classes_count.short_description = 'Classes'
    
    def verify_teachers(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} teacher(s) verified.')
    verify_teachers.short_description = 'Verify selected teachers'
    
    def unverify_teachers(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} teacher(s) unverified.')
    unverify_teachers.short_description = 'Unverify selected teachers'
    
    def delete_selected_teachers(self, request, queryset):
        """Custom delete action for teachers"""
        deleted_count = 0
        for teacher in queryset:
            try:
                # Delete the associated user too
                user = teacher.user
                teacher.delete()
                user.delete()
                deleted_count += 1
            except Exception as e:
                self.message_user(request, f'Error deleting teacher: {str(e)}', level='error')
        
        self.message_user(request, f'Successfully deleted {deleted_count} teacher(s) and their accounts.')
    delete_selected_teachers.short_description = 'Delete selected teachers and their accounts'
    
    def has_delete_permission(self, request, obj=None):
        """Only superuser can delete"""
        return request.user.is_superuser


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    """Custom admin for ClassSession model"""
    list_display = ('subject', 'class_name', 'get_teacher_name', 'get_class_key_badge', 'is_active', 'start_time', 'get_attendance_count')
    list_filter = ('is_active', 'start_time', 'class_name')
    search_fields = ('subject', 'class_name', 'teacher__user__first_name', 'class_key')
    readonly_fields = ('class_key', 'created_at', 'updated_at')
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Class Information', {
            'fields': ('teacher', 'subject', 'class_name', 'description')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('Access Control', {
            'fields': ('class_key', 'is_active', 'total_students')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_classes', 'deactivate_classes', 'generate_new_keys']
    
    def get_teacher_name(self, obj):
        return f"Prof. {obj.teacher.user.get_full_name()}"
    get_teacher_name.short_description = 'Teacher'
    
    def get_class_key_badge(self, obj):
        return format_html(
            '<span style="background-color: #d4edda; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            obj.class_key
        )
    get_class_key_badge.short_description = 'Class Key'
    
    def get_attendance_count(self, obj):
        present = obj.get_present_count()
        absent = obj.get_absent_count()
        return format_html(
            '&check; {} / &times; {}',
            present,
            absent
        )
    get_attendance_count.short_description = 'Attendance'
    
    def activate_classes(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} class(es) activated.')
    activate_classes.short_description = 'Activate selected classes'
    
    def deactivate_classes(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} class(es) deactivated.')
    deactivate_classes.short_description = 'Deactivate selected classes'
    
    def generate_new_keys(self, request, queryset):
        for session in queryset:
            session.class_key = ClassSession.generate_class_key()
            session.save()
        self.message_user(request, f'New keys generated for {queryset.count()} class(es).')
    generate_new_keys.short_description = 'Generate new class keys'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """Custom admin for AttendanceRecord model"""
    list_display = ('get_student_roll', 'get_class_info', 'get_status_badge', 'face_verified', 'marked_at')
    list_filter = ('is_present', 'face_verified', 'marked_at', 'class_session__class_name')
    search_fields = ('student__roll_number', 'student__user__first_name', 'class_session__subject')
    readonly_fields = ('marked_at', 'verification_distance')
    date_hierarchy = 'marked_at'
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'class_session', 'is_present')
        }),
        ('Face Verification', {
            'fields': ('face_verified', 'verification_distance')
        }),
        ('Device Information', {
            'fields': ('device_info', 'location'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('marked_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_roll(self, obj):
        return obj.student.roll_number
    get_student_roll.short_description = 'Roll No.'
    
    def get_class_info(self, obj):
        return f"{obj.class_session.subject} ({obj.class_session.class_name})"
    get_class_info.short_description = 'Class'
    
    def get_status_badge(self, obj):
        if obj.is_present:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Present</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">Absent</span>'
            )
    get_status_badge.short_description = 'Status'


@admin.register(FaceData)
class FaceDataAdmin(admin.ModelAdmin):
    """Admin for FaceData model"""
    list_display = ('get_user_name', 'quality_score', 'timestamp')
    list_filter = ('timestamp', 'quality_score')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('timestamp', 'image_path')
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    get_user_name.short_description = 'User'


@admin.register(ClassLog)
class ClassLogAdmin(admin.ModelAdmin):
    """Admin for ClassLog model"""
    list_display = ('get_teacher_name', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'action')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def get_teacher_name(self, obj):
        return f"Prof. {obj.teacher.user.get_full_name()}"
    get_teacher_name.short_description = 'Teacher'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin for SystemSettings model"""
    list_display = ('get_settings_display',)
    
    fieldsets = (
        ('Class Configuration', {
            'fields': ('class_key_validity_hours',)
        }),
        ('Face Recognition', {
            'fields': ('face_recognition_threshold',)
        }),
        ('Security', {
            'fields': ('max_daily_attempts', 'require_face_verification', 'enable_duplicate_detection')
        }),
        ('Last Updated', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_settings_display(self, obj):
        return 'System Configuration'
    get_settings_display.short_description = 'Settings'


# Customize admin site
admin.site.site_header = 'Attendance Management System'
admin.site.site_title = 'Admin Panel'
admin.site.index_title = 'Welcome to Attendance System Admin'
