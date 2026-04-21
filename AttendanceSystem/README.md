# Attendance Management System

A secure, Django-based attendance tracking system with **face recognition** and **unique class keys** to prevent dummy attendance marking.

## Features

### For Students
✅ **Face Registration** - Register face during signup for secure attendance marking  
✅ **Mark Attendance** - Mark attendance using unique class key + face verification  
✅ **Attendance History** - View detailed attendance records with filters  
✅ **Attendance Percentage** - Track personal attendance statistics  
✅ **Face Update** - Update or re-register face anytime  

### For Teachers
✅ **Account Verification** - Admin verification process for security  
✅ **Create Classes** - Create class sessions with date, time, and subjects  
✅ **Generate Unique Keys** - Auto-generated 6-character class keys (1-8 hour validity)  
✅ **Start/End Classes** - Control class session status  
✅ **View Attendance** - Real-time attendance marking for each class  
✅ **Attendance Reports** - Generate detailed reports with filters  
✅ **Action Logs** - Complete audit trail of all actions  

### For Administrators
✅ **User Management** - Manage students and teachers  
✅ **Teacher Verification** - Verify/unverify teacher accounts  
✅ **Class Management** - Monitor all classes and sessions  
✅ **Attendance Records** - View and manage attendance data  
✅ **System Settings** - Configure face recognition thresholds, key validity, etc.  
✅ **Reports & Analytics** - Generate system-wide reports  

## Security Features

🔒 **Face Recognition Verification** - Prevents unauthorized attendance marking  
🔒 **Unique Class Keys** - Time-limited, session-specific access codes  
🔒 **Duplicate Prevention** - Students can't mark attendance twice for same class  
🔒 **Teacher Verification** - Admin approval before teachers can create classes  
🔒 **Session Timing** - Attendance only marked during active class session  
🔒 **Face Quality Validation** - Ensures good quality face images for accuracy  

## System Architecture

```
AttendanceSystem/
├── config/                          # Django project settings
│   ├── settings.py                 # Main configuration
│   ├── urls.py                     # URL routing
│   └── wsgi.py                     # WSGI configuration
├── attendance/                      # Main app
│   ├── models.py                   # Database models
│   ├── views.py                    # View logic
│   ├── forms.py                    # Form definitions
│   ├── admin.py                    # Admin interface
│   ├── urls.py                     # App URL patterns
│   ├── face_recognition_utils.py   # Face recognition functions
│   ├── templates/                  # HTML templates
│   │   ├── base.html              # Base template
│   │   └── attendance/            # App templates
│   └── static/                     # Static files
│       ├── css/                   # Stylesheets
│       ├── js/                    # JavaScript
│       └── uploads/faces/         # Face images
├── manage.py                        # Django management script
└── requirements.txt                 # Python dependencies
```

## Database Models

### User
- Custom Django user model
- Fields: email, first_name, last_name, phone, user_type, face_encoding, face_registered
- Extends Django's AbstractUser for authentication

### Student
- Links to User
- Fields: roll_number, class_name, enrollment_date, is_verified, total_classes_attended
- Methods: get_attendance_percentage()

### Teacher
- Links to User
- Fields: employee_id, department, subject, is_verified, created_at
- Methods: get_active_classes()

### ClassSession
- Represents a single class period
- Fields: teacher, subject, class_name, class_key, start_time, end_time, duration_minutes, is_active
- Methods: generate_class_key(), is_valid_for_attendance(), get_present_count(), get_absent_count()

### AttendanceRecord
- Tracks student attendance
- Fields: student, class_session, is_present, marked_at, face_verified, verification_distance
- Unique together: (student, class_session)

### FaceData
- Stores face encodings for verification
- Fields: user, face_encoding, image_path, timestamp, quality_score

### ClassLog
- Audit trail for teacher actions
- Fields: teacher, class_session, action, description, timestamp, ip_address

### SystemSettings
- Global configuration
- Fields: class_key_validity_hours, face_recognition_threshold, max_daily_attempts, etc.

## Installation & Setup

### 1. Clone or Download the Project
```bash
cd AttendanceSystem
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** The `face_recognition` library requires `dlib` which may need:
- **Windows**: Download pre-compiled wheels from [here](https://github.com/ageitgey/face_recognition/issues/175)
- **Linux**: `sudo apt-get install build-essential cmake dlib-dev`
- **Mac**: `brew install cmake`

### 4. Database Migration
```bash
python manage.py migrate
```

### 5. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

## Usage Guide

### Student Workflow

1. **Register Account**
   - Go to Student Registration
   - Fill form: Name, Roll Number, Class, Email, Password
   - Complete registration

2. **Register Face** (Recommended for security)
   - Go to "Register Face" after login
   - Upload or capture a clear photo
   - Face will be verified and stored

3. **Mark Attendance**
   - Click "Mark Attendance"
   - Enter unique class key (provided by teacher)
   - Optional: Scan face for verification
   - Attendance marked successfully

4. **View History**
   - Check "Attendance History" to view all records
   - Filter by date, class, or subject
   - See attendance percentage

### Teacher Workflow

1. **Register Account**
   - Go to Teacher Registration
   - Fill form: Name, Employee ID, Department, Subject, Email, Password
   - Account pending verification

2. **Wait for Admin Verification**
   - Admin verifies account in admin panel
   - You'll receive notification when verified

3. **Create Class Session**
   - Click "Create Class"
   - Enter: Subject, Class Name, Start Time, End Time, Duration
   - System auto-generates unique class key

4. **Start Class**
   - Click on class and select "Start Class"
   - Share the unique key with students
   - Students can now mark attendance

5. **End Class**
   - Click "End Class" when class ends
   - Attendance marking is closed

6. **View Reports**
   - Check "Attendance Report"
   - Filter by date, class, or subject
   - Export or print reports

### Admin Workflow

1. **Access Admin Panel**
   - Go to `/admin/`
   - Login with superuser account

2. **Verify Teachers**
   - Go to Teachers section
   - Select unverified teachers
   - Click "Verify selected teachers"

3. **Manage Classes**
   - View all classes and sessions
   - Activate/deactivate classes
   - Generate new keys if needed
   - View class-wise attendance

4. **Monitor Attendance**
   - Check attendance records
   - View student statistics
   - Identify patterns

5. **Configure System**
   - Go to System Settings
   - Adjust face recognition threshold
   - Set key validity duration
   - Enable/disable features

## API Endpoints

### Mark Attendance (POST)
```
/api/mark-attendance/
Body: {
  "class_key": "ABC123",
  "face_image": "base64_encoded_image"
}
```

### Verify Class Key (POST)
```
/api/verify-class-key/
Body: {
  "class_key": "ABC123"
}
```

## Configuration

Edit `config/settings.py` for:

```python
# Face Recognition
FACE_RECOGNITION_TOLERANCE = 0.6  # Lower = stricter matching
FACE_RECOGNITION_MODEL = 'cnn'     # 'hog' for speed, 'cnn' for accuracy

# Class Keys
CLASS_KEY_LENGTH = 6
CLASS_KEY_EXPIRY_HOURS = 8

# Session
SESSION_COOKIE_AGE = 86400  # 24 hours
```

## File Structure for Uploads

```
AttendanceSystem/
└── media/
    └── face_images/
        └── 2024/01/20/
            └── user_face.jpg
```

## Troubleshooting

### Face Recognition Not Working
- Ensure good lighting when capturing face
- Keep face clear and frontal
- Image should be at least 100x100 pixels
- Try adjusting `FACE_RECOGNITION_TOLERANCE` in settings

### Class Key Not Valid
- Check if class session is active
- Verify class hasn't ended
- Ensure key is within validity period (default 8 hours)

### Teacher Can't Create Classes
- Confirm teacher account is verified in admin
- Check if user_type is set to 'teacher'

### Database Issues
- Run migrations: `python manage.py migrate`
- Clear migrations: `python manage.py migrate --reset attendance`
- Backup database before migrations

## Performance Tips

1. **Face Recognition Speed**
   - Use 'hog' model for speed over accuracy
   - Reduce image resolution before processing

2. **Database Optimization**
   - Add indexes to frequently queried fields (done in models)
   - Archive old attendance records

3. **File Upload**
   - Limit image size to 5MB
   - Compress images before upload
   - Use CDN for static files

## Security Best Practices

1. **Change SECRET_KEY in production**
   ```python
   SECRET_KEY = 'your-very-secret-key-here'
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   ```

2. **Use HTTPS in production**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

3. **Database backup**
   ```bash
   python manage.py dumpdata > backup.json
   ```

4. **Regular updates**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## Deployment

### Using Gunicorn & Nginx

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

3. **Configure Nginx** as reverse proxy
   - Forward requests to Gunicorn
   - Serve static files directly

4. **Use Supervisor** to keep running

## Support & Contribution

For issues or contributions, please:
1. Check existing issues
2. Provide detailed error messages
3. Include system information
4. Submit pull requests with tests

## License

MIT License - Use freely for educational and commercial purposes

## Future Enhancements

- [ ] Mobile app for students
- [ ] SMS/Email notifications
- [ ] Multi-factor authentication
- [ ] QR code attendance
- [ ] Biometric (fingerprint) verification
- [ ] Calendar integration
- [ ] API rate limiting
- [ ] Advanced analytics & ML predictions
- [ ] Voice-based attendance
- [ ] Geolocation verification

---

**Version:** 1.0.0  
**Last Updated:** January 2026
