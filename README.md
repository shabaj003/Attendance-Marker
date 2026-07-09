# 📋 Attendance Management System

A role-based Django web application that digitizes classroom attendance with recurring class scheduling, daily key rotation, and face-assisted verification to prevent proxy attendance.

🔗 Live Demo:  https://attendance-marker-f8ra.onrender.com/
📸 Screenshots: <img width="2556" height="1263" alt="Screenshot (221)" src="https://github.com/user-attachments/assets/f37ef6a8-4ab0-46e7-a4b6-729432a1db02" />
<img width="2560" height="1269" alt="Screenshot (222)" src="https://github.com/user-attachments/assets/400e3106-d365-46b3-b6cb-26d5e13ea88d" />
<img width="2554" height="1275" alt="Screenshot (224)" src="https://github.com/user-attachments/assets/7ffe20d2-2b2c-47d3-9cee-8bcf7bf6c401" />


---

## Overview

Manual classroom attendance is slow and vulnerable to proxy marking. This system provides a secure, structured workflow for Students, Teachers, and Admins — combining daily-rotating access keys with optional face verification to enforce attendance integrity.

## Features

- 👥 **Role-based access** — separate dashboards and permissions for Students, Teachers, and Admins
- 🔁 **Recurring class scheduling** — teachers set a date range once instead of creating sessions daily
- 🔑 **Daily key rotation** — a fresh, time-bound class key is generated each time a teacher starts a session
- 📸 **Face verification** — OpenCV-based face detection and encoding comparison as an anti-proxy layer
- 🚫 **Duplicate prevention** — one attendance record per student, per class, per day, enforced at the database level
- ✅ **Teacher verification gate** — admins approve teachers before they can manage classes
- 📊 **Attendance reporting** — filterable history for students and teachers, with status breakdowns
- 📝 **Audit logging** — every class action (created/started/ended) is logged with timestamp and IP

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2.7, Django REST Framework |
| Database | SQLite (dev) |
| Face Processing | OpenCV, NumPy, Pillow, SciPy |
| Frontend | Django Templates, Bootstrap 5, jQuery, Vanilla JS |
| Server | Gunicorn (deployment-ready) |

## Architecture

Follows Django's MVT (Model-View-Template) pattern with a distinct face-processing layer:

```
Presentation Layer   → Django Templates + Bootstrap + JS (camera capture UX)
Application Layer    → Django Views (auth, scheduling, attendance, reporting)
Data Layer           → Django ORM → SQLite
Face Processing Layer→ OpenCV (detection) + encoding comparison
Admin Layer          → Django Admin with custom ModelAdmin actions
```

## Data Model Highlights

- **User** — custom model extending `AbstractUser` with `user_type` (student/teacher/admin) and face metadata
- **ClassSession** — supports recurring schedules (`schedule_start_date`, `schedule_end_date`, daily time windows) plus daily runtime state (`active_date`, `class_key`)
- **AttendanceRecord** — enforces uniqueness on `(student, class_session, session_date)`, stores face verification distance and captured image
- **FaceData** — stores per-user face encoding with a quality score
- **ClassLog** — audit trail of teacher actions for accountability

## Core Workflow

1. Teacher creates a recurring schedule for a date range (e.g., a semester)
2. Each day, the teacher clicks **Start Class** → system generates a fresh class key valid for that session
3. Students enter the key within the active time window
4. If face verification is enabled, the student's live capture is compared against their registered face encoding
5. Attendance is recorded — duplicate entries for the same day are blocked automatically

## Getting Started

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/mark-attendance/` | Submit attendance with class key + optional face data |
| POST | `/api/verify-class-key/` | Validate a class key before submission |

## Security Controls

- Role-based route protection (`login_required` + user type checks)
- Teacher verification required before any class management action
- POST-only state transitions for starting/ending classes
- CSRF middleware enabled
- HttpOnly, SameSite-strict session cookies
- Database-level duplicate attendance prevention

## Known Limitations & Roadmap

- [ ] Move from SQLite to PostgreSQL for concurrent production use
- [ ] Add real face-embedding model with liveness detection (current approach uses simplified encoding comparison)
- [ ] Add automated test coverage for role access and time-window edge cases
- [ ] Harden production settings (`DEBUG=False`, restricted `ALLOWED_HOSTS`, env-based secret key)
- [ ] Add QR/NFC as an alternative attendance method
- [ ] Department-wise analytics dashboards

## Disclaimer

This project was built as a learning exercise in secure, role-based web application design. The face verification module is intentionally lightweight (Haar cascade + Euclidean distance) and is not intended as a production-grade biometric security system.

---

*Built to explore role-based access control, recurring scheduling logic, and computer-vision-assisted verification in a Django application.*
