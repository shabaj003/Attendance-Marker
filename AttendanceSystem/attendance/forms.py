"""
Forms for Attendance Management System
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User, Student, Teacher, AttendanceRecord, ClassSession
import re


class BaseUserForm(forms.ModelForm):
    """Base form for user registration"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'minlength': '8',
            'autocomplete': 'off'
        }),
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'off'
        }),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'autocomplete': 'off'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
        }
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone.replace('-', '').replace(' ', '')):
            raise ValidationError('Please enter a valid phone number.')
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class StudentRegistrationForm(BaseUserForm):
    """Student registration form"""
    roll_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Roll Number (e.g., 001A)',
            'pattern': '[A-Z0-9]+'
        }),
        help_text='Roll number must contain only letters and numbers'
    )
    class_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Class Name (e.g., 10-A, 12-B)'
        })
    )
    face_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Upload a clear photo of your face (JPG, PNG, etc.)'
    )
    
    class Meta(BaseUserForm.Meta):
        fields = ('email', 'first_name', 'last_name', 'phone', 'roll_number', 'class_name', 'face_image')
    
    def __init__(self, *args, **kwargs):
        self.face_image_data = kwargs.pop('face_image_data', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        face_image = cleaned_data.get('face_image')
        face_image_data = self.face_image_data
        
        if not face_image and not face_image_data:
            raise forms.ValidationError('Please provide a face image either by uploading a file or capturing from camera.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.username = self.cleaned_data['email'].split('@')[0] + str(User.objects.count())
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'].upper(),
                class_name=self.cleaned_data['class_name']
            )
        return user


class TeacherRegistrationForm(BaseUserForm):
    """Teacher registration form"""
    employee_id = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Employee ID'
        })
    )
    department = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department'
        })
    )
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject Taught'
        })
    )
    
    class Meta(BaseUserForm.Meta):
        fields = ('email', 'first_name', 'last_name', 'phone', 'employee_id', 'department', 'subject')
    
    def clean_employee_id(self):
        """Validate employee ID uniqueness"""
        emp_id = self.cleaned_data.get('employee_id')
        if Teacher.objects.filter(employee_id=emp_id).exists():
            raise ValidationError('This employee ID is already registered.')
        return emp_id
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'teacher'
        user.username = 'teacher_' + self.cleaned_data['employee_id']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            Teacher.objects.create(
                user=user,
                employee_id=self.cleaned_data['employee_id'],
                department=self.cleaned_data['department'],
                subject=self.cleaned_data['subject']
            )
        return user


class UserLoginForm(forms.Form):
    """Login form for all users"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'off'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class FaceRegistrationForm(forms.Form):
    """Form for face registration during signup"""
    face_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'
        }),
        help_text='Upload a clear photo of your face'
    )
    
    def clean_face_image(self):
        """Validate face image"""
        image = self.cleaned_data.get('face_image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image size must be less than 5MB')
        return image


class CreateClassSessionForm(forms.ModelForm):
    """Form for teachers to create class sessions"""
    duration_minutes = forms.IntegerField(
        min_value=15,
        max_value=480,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Duration in minutes (15-480)',
            'step': '15'
        }),
        help_text='Class duration in minutes'
    )
    
    class Meta:
        model = ClassSession
        fields = ('subject', 'class_name', 'start_time', 'end_time', 'description')
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject Name'
            }),
            'class_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Class Name (e.g., 10-A)'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional: Class description or topics'
            }),
        }


class MarkAttendanceForm(forms.ModelForm):
    """Form for students to mark attendance"""
    class_key = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Class Key (provided by teacher)',
            'autofocus': 'autofocus'
        }),
        help_text='6-character unique code provided by your teacher'
    )
    
    class Meta:
        model = AttendanceRecord
        fields = []
    
    def clean_class_key(self):
        """Validate class key"""
        class_key = self.cleaned_data.get('class_key').upper()
        
        try:
            class_session = ClassSession.objects.get(class_key=class_key)
            if not class_session.is_valid_for_attendance():
                raise ValidationError('This class session is not active for attendance.')
        except ClassSession.DoesNotExist:
            raise ValidationError('Invalid class key. Please check with your teacher.')
        
        return class_key


class CustomUserChangeForm(UserChangeForm):
    """Custom form for editing user profile"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AttendanceFilterForm(forms.Form):
    """Form for filtering attendance records"""
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False,
        label='From Date'
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        required=False,
        label='To Date'
    )
    class_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by class'
        }),
        required=False,
        label='Class Name'
    )
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by subject'
        }),
        required=False,
        label='Subject'
    )
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by subject'
        }),
        required=False
    )
