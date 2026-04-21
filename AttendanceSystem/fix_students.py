#!/usr/bin/env python
"""
Fix script to create missing Student profiles for student users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from attendance.models import User, Student

# Get all student users
student_users = User.objects.filter(user_type='student')
print(f"Total student users: {student_users.count()}")

# Get student profiles
student_profiles = Student.objects.all()
print(f"Total student profiles: {student_profiles.count()}")

# Find students without profiles and create them
fixed_count = 0
for user in student_users:
    try:
        student = Student.objects.get(user=user)
        print(f"✓ {user.username} has profile")
    except Student.DoesNotExist:
        print(f"✗ {user.username} MISSING profile - creating it...")
        Student.objects.create(
            user=user,
            roll_number=f"AUTO-{user.id}",
            class_name="Not Set"
        )
        print(f"  → Created profile for {user.username}")
        fixed_count += 1

print(f"\nFixed {fixed_count} student(s)")
