# Quick Start Guide

## 5-Minute Setup

### Windows Users
```batch
cd AttendanceSystem
setup.bat
```

### Linux/Mac Users
```bash
cd AttendanceSystem
chmod +x setup.sh
./setup.sh
```

## Start Development Server

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run server
python manage.py runserver
```

## Access Points

- **Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Student Registration**: http://localhost:8000/student-register/
- **Teacher Registration**: http://localhost:8000/teacher-register/
- **Login**: http://localhost:8000/login/

## Default Login

Use the superuser account created during setup:
- Username/Email: (as created)
- Password: (as created)

## Create Your First Class

### Step 1: Login as Teacher
1. Go to http://localhost:8000/login/
2. Click "Teacher Register" to create a teacher account
3. Wait for admin verification (you can do this in admin panel)

### Step 2: Create a Class
1. Go to Teacher Dashboard
2. Click "Create Class Session"
3. Fill in:
   - Subject: "Mathematics"
   - Class: "10-A"
   - Start Time: 2026-01-20 10:00
   - End Time: 2026-01-20 11:00
4. Click "Create Class Session"

### Step 3: Start the Class
1. Click on the class you created
2. Click "Start Class"
3. Share the unique class key with students

### Step 4: Mark Attendance as Student
1. Go to http://localhost:8000/login/ (different tab/browser)
2. Register as a student
3. Go to "Mark Attendance"
4. Enter the class key
5. Submit

## File Structure

```
AttendanceSystem/
├── config/              # Django configuration
├── attendance/          # Main app
│   ├── models.py       # Database models
│   ├── views.py        # Application logic
│   ├── forms.py        # Form handling
│   ├── urls.py         # URL routing
│   ├── admin.py        # Admin interface
│   ├── templates/      # HTML templates
│   └── static/         # CSS, JS, images
├── manage.py           # Django management
├── requirements.txt    # Dependencies
├── README.md          # Full documentation
└── INSTALLATION.md    # Installation guide
```

## Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Reset database
python manage.py flush

# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json
```

## Deactivate Virtual Environment

```bash
# Windows/Linux/Mac
deactivate
```

## Stop Development Server

```bash
# Press Ctrl+C in terminal
```

## Admin Panel Tasks

### Verify Teachers
1. Go to `/admin/`
2. Click "Teachers"
3. Select unverified teachers
4. Click "Verify selected teachers"
5. Click "Go"

### View Attendance
1. Go to `/admin/`
2. Click "Attendance Records"
3. View all attendance marks
4. Filter by date, class, or status

### Manage System Settings
1. Go to `/admin/`
2. Click "System Settings"
3. Adjust thresholds and configuration

## Security Notes

⚠️ **Development Only:**
```python
# In config/settings.py (development)
DEBUG = True
ALLOWED_HOSTS = ['*']
```

⚠️ **Production:**
```python
# In config/settings.py (production)
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-secret-key'
SECURE_SSL_REDIRECT = True
```

## Troubleshooting

### Virtual Environment Not Activating
```bash
# Windows
python -m venv venv
venv\Scripts\activate.bat

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Port 8000 Already in Use
```bash
# Change port
python manage.py runserver 8001
```

### Database Not Found
```bash
# Run migrations
python manage.py migrate
```

### Face Recognition Not Working
- Ensure good lighting
- Take clear frontal photos
- Check settings.py for FACE_RECOGNITION_TOLERANCE

## Next Steps

1. ✅ Run setup
2. ✅ Create test accounts
3. ✅ Create test class
4. ✅ Mark test attendance
5. Read full [README.md](README.md)
6. Refer to [INSTALLATION.md](INSTALLATION.md) for production

## Features Overview

### Student Features
- ✓ User registration with email
- ✓ Face registration for security
- ✓ Mark attendance with unique class key
- ✓ Face verification during attendance
- ✓ View attendance history
- ✓ Track attendance percentage

### Teacher Features
- ✓ Teacher registration
- ✓ Admin verification process
- ✓ Create class sessions
- ✓ Generate unique 6-char keys
- ✓ Start/end classes
- ✓ View real-time attendance
- ✓ Generate attendance reports
- ✓ Action audit logs

### Admin Features
- ✓ User management
- ✓ Teacher verification
- ✓ Class management
- ✓ Attendance monitoring
- ✓ System configuration
- ✓ Reports and analytics

## Support

- Full README: [README.md](README.md)
- Installation Help: [INSTALLATION.md](INSTALLATION.md)
- Code Documentation: Check docstrings in code

---

**Happy coding!** 🎉
