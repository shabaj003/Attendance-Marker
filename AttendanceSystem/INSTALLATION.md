# Installation Guide - Attendance Management System

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB
- **Storage**: 500MB for installation
- **OS**: Windows, Linux, or macOS

## Prerequisites

### Windows
1. Download Python 3.9+ from [python.org](https://www.python.org/)
2. During installation, check "Add Python to PATH"
3. Install Visual C++ Build Tools (for dlib compilation)

### Linux
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install build-essential cmake dlib-dev
```

### macOS
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake python3
```

## Installation Steps

### Option 1: Automated Setup (Windows)

1. **Navigate to project folder**
   ```bash
   cd AttendanceSystem
   ```

2. **Run setup script**
   ```bash
   setup.bat
   ```

3. **Follow the prompts** to create superuser account

### Option 2: Automated Setup (Linux/Mac)

1. **Navigate to project folder**
   ```bash
   cd AttendanceSystem
   ```

2. **Make script executable**
   ```bash
   chmod +x setup.sh
   ```

3. **Run setup script**
   ```bash
   ./setup.sh
   ```

### Option 3: Manual Setup

#### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Troubleshooting face_recognition installation:**

If you encounter issues installing `face_recognition`:

**Windows:**
- Download pre-compiled dlib wheel from [here](https://github.com/ageitgey/face_recognition/issues/175)
- Install: `pip install dlib-19.24.4-cp39-cp39-win_amd64.whl`
- Then: `pip install face_recognition`

**Linux:**
```bash
sudo apt-get install build-essential cmake dlib-dev
pip install face_recognition
```

**macOS:**
```bash
brew install cmake
pip install face_recognition
```

#### Step 3: Initialize Database
```bash
python manage.py migrate
```

#### Step 4: Create Admin Account
```bash
python manage.py createsuperuser
```

Enter your credentials:
- Username: (your preferred admin username)
- Email: admin@attendance.com
- Password: (strong password)

#### Step 5: Run Development Server
```bash
python manage.py runserver
```

Access the application at: **http://localhost:8000**

## First-Time Setup

### 1. Login to Admin Panel
- Visit: http://localhost:8000/admin/
- Use superuser credentials created during setup

### 2. Create System Settings
- Go to "System Settings"
- Configure default values:
  - Face recognition threshold: 0.6
  - Class key validity: 8 hours
  - Max daily attempts: 5

### 3. Create a Test Teacher (Optional)
- Go to "Teachers"
- Add a new teacher manually
- Mark as "verified"

### 4. Test the System
- Register a student account
- Register a teacher account  
- Create a class session
- Mark attendance

## Database Backup

### Backup Database
```bash
python manage.py dumpdata > backup.json
```

### Restore Database
```bash
python manage.py loaddata backup.json
```

## Static Files & Media

### Collect Static Files (for production)
```bash
python manage.py collectstatic
```

### File Uploads
- **Face images**: Stored in `media/face_images/`
- **Max size**: 5MB
- **Supported formats**: JPG, PNG, GIF

## Production Deployment

### Using Gunicorn

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Update settings.py**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   SECRET_KEY = 'your-very-long-secret-key'
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

### Using Nginx

1. **Install Nginx**
   ```bash
   sudo apt-get install nginx
   ```

2. **Create config file** (`/etc/nginx/sites-available/attendance`)
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location /static/ {
           alias /path/to/AttendanceSystem/staticfiles/;
       }

       location /media/ {
           alias /path/to/AttendanceSystem/media/;
       }

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/attendance /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Using Supervisor

1. **Install Supervisor**
   ```bash
   sudo apt-get install supervisor
   ```

2. **Create config** (`/etc/supervisor/conf.d/attendance.conf`)
   ```ini
   [program:attendance]
   directory=/path/to/AttendanceSystem
   command=/path/to/venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/attendance.log
   ```

3. **Start service**
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start attendance
   ```

## Environment Variables

Create `.env` file for sensitive data:

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

Load in settings.py:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

## SSL/HTTPS Setup

Using Let's Encrypt with Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

Update Nginx config:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
}
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Database Locked
```bash
# Remove old SQLite lock file
rm db.sqlite3-shm
rm db.sqlite3-wal
```

### Permission Denied (Media Uploads)
```bash
# Set permissions
chmod -R 755 media/
```

### Face Recognition Errors
- Ensure good lighting in images
- Try reducing FACE_RECOGNITION_TOLERANCE in settings.py
- Check image quality (min 100x100 pixels)

### Import Errors
```bash
# Verify virtual environment is activated
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## Updating System

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Update Django & Apps
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

## Logs & Monitoring

### View Application Logs
```bash
tail -f /var/log/attendance.log
```

### Django Debug Toolbar (Development Only)
```bash
pip install django-debug-toolbar
```

Add to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]
```

## Support

For installation issues:
1. Check Python version: `python --version`
2. Verify virtual environment is activated
3. Check error messages in console
4. Refer to specific package documentation

## Next Steps

1. ✅ Installation complete
2. Create test accounts
3. Configure email for notifications
4. Set up backups
5. Monitor system usage
6. Plan scaling strategy

---

**Questions?** Refer to README.md for more information.
