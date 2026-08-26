# BIT Mesra Hostel Maintenance Portal

A simple web application for handling hostel maintenance complaints from submission to resolution.

The idea is straightforward: a student reports a problem, the complaint is routed to the appropriate hostel warden, maintenance staff can be assigned, the status can be updated, and the student can track what happened.

The project is built as a small Flask application with SQLite and a server-rendered HTML frontend. It does not use React, Node.js, MongoDB, AI/ML, or a separate frontend framework.

> **Project note:** This is a student-built/demo application inspired by the hostel maintenance workflow at BIT Mesra. The demo administrator and warden accounts in the local database are not official BIT Mesra staff accounts.

---

## Main Features

### Student

- Student registration with:
  - Full name
  - Roll number
  - BIT Mesra institute email
  - Hostel
  - Password
- Login and logout
- Forgot-password flow
- Student dashboard
- Hostel shown from the student's profile
- Submit maintenance complaints
- Complaint categories
- Priority selection
- Complaint status tracking
- Complaint history
- View resolution notes
- Students can only see their own complaints
- Students cannot submit a complaint for another hostel

### Warden

- Separate warden login
- Every demo warden is mapped to one hostel
- Warden dashboard
- Hostel-specific complaint list
- Complaint search
- Status filter
- Priority filter
- Category filter
- View complaint details
- Assign maintenance staff
- Move complaints to `In Progress`
- Add resolution notes
- Mark complaints as `Resolved`
- View complaint history
- A warden cannot view or update complaints from another hostel

### Administrator

- Administrator login
- All-hostel complaint view
- Overall complaint statistics
- Student directory
- Warden assignment directory
- View and manage complaints across all hostels

### Complaint workflow

```text
Student reports issue
        |
        v
Complaint created as Pending
        |
        v
Warden reviews complaint
        |
        v
Maintenance staff assigned
        |
        v
In Progress
        |
        v
Work completed
        |
        v
Resolution note added
        |
        v
Resolved
```

---

# Technology Stack

## Backend

### Python
Main programming language.

Used for:
- Server-side application logic
- Authentication
- Database operations
- Validation
- Complaint workflow
- Role-based access control

### Flask
Lightweight Python web framework.

Used for:
- HTTP routes
- API endpoints
- Sessions
- Rendering `index.html`
- Request/response handling

Main backend endpoints include:

```text
/api/signup
/api/login
/api/logout
/api/me

/api/complaints
/api/complaints/<id>
/api/complaints/<id>/history

/api/dashboard

/api/students
/api/wardens

/api/forgot-password
```

### Werkzeug
Used through Flask for secure password hashing and password verification.

Main functions:

```python
generate_password_hash()
check_password_hash()
```

Passwords are stored as hashes rather than plain text.

---

## Database

### SQLite

The application uses SQLite for local storage.

Main database:

```text
database.db
```

Main tables:

### `users`

Stores students, wardens and the administrator.

Important fields:

```text
id
full_name
roll_number
email
password
role
assigned_hostel
```

### `complaints`

Stores maintenance complaints.

Important fields:

```text
id
student_name
roll_number
college_email
hostel_name
room_number
category
priority
issue_title
issue_description
assigned_staff
resolution_note
status
date_submitted
date_updated
```

### `complaint_history`

Stores the timeline of a complaint.

Important fields:

```text
id
complaint_id
status
changed_by
note
changed_at
```

Relationship:

```text
complaints
    |
    | 1-to-many
    v
complaint_history
```

---

## Frontend

The frontend is intentionally simple and framework-free.

### HTML5

Used for:
- Page structure
- Forms
- Tables
- Dashboard sections
- Complaint modal

### Tailwind CSS

Tailwind CSS is loaded from the CDN and is used for the UI layout and styling.

Used for:
- Responsive layout
- Cards
- Tables
- Forms
- Buttons
- Status badges
- Dashboard styling

### Vanilla JavaScript

No React or Vue is used.

JavaScript handles:

- Login/signup requests
- Logout
- Forgot-password requests
- Complaint submission
- Complaint loading
- Dashboard updates
- Filters
- Complaint modal
- Complaint history
- Warden assignment display
- Student directory display

### SweetAlert2

Used for:
- Success messages
- Error messages
- Login feedback
- Complaint submission feedback
- Password reset feedback

### Feather Icons

Used for lightweight interface icons.

---

# System Architecture

The project follows a simple three-layer web application structure.

```text
                    +----------------------+
                    |      Browser         |
                    |----------------------|
                    | HTML                 |
                    | Tailwind CSS         |
                    | Vanilla JavaScript   |
                    | SweetAlert2          |
                    | Feather Icons        |
                    +----------+-----------+
                               |
                               | HTTP / JSON
                               v
                    +----------------------+
                    |      Flask App       |
                    |----------------------|
                    | Authentication       |
                    | Session Management   |
                    | Access Control       |
                    | Complaint APIs       |
                    | Dashboard APIs       |
                    | Validation           |
                    +----------+-----------+
                               |
                               | SQL
                               v
                    +----------------------+
                    |       SQLite         |
                    |----------------------|
                    | users                |
                    | complaints           |
                    | complaint_history    |
                    +----------------------+
```

---

# Access Control Architecture

The important part of the application is that hostel access is controlled on the backend, not only in the frontend.

## Student

```text
Student Login
     |
     v
assigned_hostel stored in session
     |
     v
Student creates complaint
     |
     v
Backend takes hostel from session
     |
     v
Complaint stored with that hostel
```

The student does not control the hostel value sent to the database.

## Warden

```text
Warden Login
     |
     v
assigned_hostel stored in session
     |
     v
Query complaints
     |
     v
WHERE hostel_name = assigned_hostel
```

Example:

```text
hostel1.warden.demo@bitmesra.ac.in
                    |
                    v
                   H1
                    |
                    v
          H1 complaints only
```

A warden assigned to H2 cannot access H1 complaints through the backend.

## Administrator

```text
Admin Login
     |
     v
No hostel restriction
     |
     v
All-hostel complaints
```

---

# Roles

The application uses three roles:

```text
student
warden
admin
```

### Student permissions

| Action | Student |
|---|---|
| Register | Yes |
| Login | Yes |
| Submit complaint | Yes |
| View own complaints | Yes |
| View another student's complaints | No |
| Update complaint | No |
| Manage staff assignment | No |
| View all hostels | No |

### Warden permissions

| Action | Warden |
|---|---|
| Login | Yes |
| View assigned-hostel complaints | Yes |
| View another hostel's complaints | No |
| Assign maintenance staff | Yes |
| Change status | Yes |
| Add resolution note | Yes |
| Reject complaint | No |
| View student directory | No |
| View all hostel statistics | No |

### Administrator permissions

| Action | Administrator |
|---|---|
| Login | Yes |
| View all complaints | Yes |
| Manage complaints | Yes |
| Reject complaints | Yes |
| View student directory | Yes |
| View warden assignments | Yes |
| View all hostel statistics | Yes |

---

# Complaint Categories

The application provides the following maintenance categories:

```text
Electrical / Power
Wi-Fi / Internet
Plumbing / Water
Washroom / Hygiene
Furniture / Room
Washing Machine
Geyser
Cleaning
Pest Control
Other
```

---

# Priority Levels

```text
Low
Medium
High
Urgent
```

---

# Complaint Status

```text
Pending
In Progress
Resolved
Rejected
```

The backend also applies workflow rules:

- A complaint cannot move to `In Progress` without assigning maintenance staff.
- A complaint cannot be marked `Resolved` without a resolution note.
- Wardens cannot reject complaints.
- Administrators can reject complaints.

---

# Project Structure

```text
BIT-Mesra-Hostel-Maintenance/
│
├── app.py
├── init_db.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   └── bit.jpeg
│
└── templates/
    └── index.html
```

During local development the following file is also generated:

```text
database.db
```

It should not be committed to GitHub.

---

# Setup

## 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd BIT-Mesra-Hostel-Maintenance
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Initialize the database

```powershell
python init_db.py
```

This creates a fresh local development database.

It creates:

- 1 demo administrator
- 14 demo warden accounts
- H1-H14 hostel assignments
- Complaint tables
- Complaint history table

> Running `init_db.py` resets the local database, so existing test students and complaints will be removed.

## 5. Start the server

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# Demo Accounts

These are **local demo accounts created by `init_db.py`**. They are not official BIT Mesra credentials.

## Administrator

```text
Email: admin.demo@bitmesra.ac.in
Password: BITMesra@2026
```

## Wardens

All demo wardens use:

```text
Password: BITMesra@2026
```

Mappings:

```text
Hostel 1  -> hostel1.warden.demo@bitmesra.ac.in
Hostel 2  -> hostel2.warden.demo@bitmesra.ac.in
Hostel 3  -> hostel3.warden.demo@bitmesra.ac.in
Hostel 4  -> hostel4.warden.demo@bitmesra.ac.in
Hostel 5  -> hostel5.warden.demo@bitmesra.ac.in
Hostel 6  -> hostel6.warden.demo@bitmesra.ac.in
Hostel 7  -> hostel7.warden.demo@bitmesra.ac.in
Hostel 8  -> hostel8.warden.demo@bitmesra.ac.in
Hostel 9  -> hostel9.warden.demo@bitmesra.ac.in
Hostel 10 -> hostel10.warden.demo@bitmesra.ac.in
Hostel 11 -> hostel11.warden.demo@bitmesra.ac.in
Hostel 12 -> hostel12.warden.demo@bitmesra.ac.in
Hostel 13 -> hostel13.warden.demo@bitmesra.ac.in
Hostel 14 -> hostel14.warden.demo@bitmesra.ac.in
```

---

# Security and Validation

The project includes several basic protections suitable for a local academic/demo application.

### Password hashing

Passwords are hashed using Werkzeug before storage.

### Session-based authentication

The Flask session stores the logged-in user's:

```text
user_id
role
full_name
email
roll_number
assigned_hostel
```

### Role-based access control

The backend checks whether the current user is:

```text
student
warden
admin
```

before serving protected resources.

### Hostel-based access control

Warden complaint queries are restricted to the warden's assigned hostel on the server.

### Backend validation

The backend validates:

- Required fields
- BIT Mesra email domain
- Valid hostel
- Valid category
- Valid priority
- Valid status
- Valid maintenance staff

### HTML escaping

User-entered values rendered in tables are escaped on the frontend before insertion into HTML.

---

# Application Flow

## Registration

```text
Student
   |
   v
Create Account
   |
   +--> Full Name
   +--> Roll Number
   +--> Hostel
   +--> Institute Email
   +--> Password
   |
   v
Flask validation
   |
   v
Password hashing
   |
   v
SQLite users table
```

## Login

```text
Email + Password
       |
       v
Flask
       |
       v
SQLite users
       |
       v
Password verification
       |
       v
Session created
       |
       v
Dashboard
```

## Complaint submission

```text
Student
   |
   v
Complaint Form
   |
   +--> Room
   +--> Category
   +--> Priority
   +--> Issue Title
   +--> Description
   |
   v
Flask
   |
   v
Student's assigned hostel
   |
   v
complaints table
   |
   v
complaint_history table
```

## Complaint management

```text
Warden
  |
  v
Only assigned-hostel complaints
  |
  v
Open complaint
  |
  +--> Assign maintenance staff
  |
  +--> Change status
  |
  +--> Add resolution note
  |
  v
Complaint history updated
```

---

# API Overview

## Authentication

### `POST /api/signup`

Creates a student account.

### `POST /api/login`

Authenticates a user and creates a session.

### `POST /api/logout`

Clears the current session.

### `GET /api/me`

Returns information about the logged-in user.

### `POST /api/forgot-password`

Resets a supported user password after validating the required account details.

---

## Complaints

### `GET /api/complaints`

Returns:

- own complaints for a student
- assigned-hostel complaints for a warden
- all complaints for an administrator

### `POST /api/complaints`

Creates a new maintenance complaint.

### `PATCH /api/complaints/<id>`

Updates:

- status
- maintenance assignment
- resolution note

### `GET /api/complaints/<id>/history`

Returns the complaint's status history.

---

## Dashboard

### `GET /api/dashboard`

Returns complaint statistics such as:

```text
total
pending
in_progress
resolved
urgent
by_category
by_hostel
```

The response is hostel-scoped for wardens and global for administrators.

---

## Admin

### `GET /api/students`

Returns the registered student directory.

### `GET /api/wardens`

Returns the demo warden directory with assigned hostels.

---

# Database Relationships

```text
+---------------------+
|       users         |
+---------------------+
| id                  |
| full_name           |
| roll_number         |
| email               |
| password            |
| role                |
| assigned_hostel     |
+----------+----------+
           |
           |
           | student submits
           v
+---------------------+
|     complaints      |
+---------------------+
| id                  |
| student_name        |
| roll_number         |
| college_email       |
| hostel_name         |
| room_number         |
| category            |
| priority            |
| issue_title         |
| issue_description   |
| assigned_staff      |
| resolution_note     |
| status              |
| date_submitted      |
| date_updated        |
+----------+----------+
           |
           | 1 : many
           v
+---------------------+
| complaint_history   |
+---------------------+
| id                  |
| complaint_id        |
| status              |
| changed_by          |
| note                |
| changed_at          |
+---------------------+
```

---

# Why the project uses SQLite

SQLite is sufficient for the current scope because the application is a small local Flask project and does not need a separate database server.

The schema is also easy to inspect and reset during development.

For a larger production deployment, the database layer could be moved to PostgreSQL without changing the overall application workflow.

---

# Testing Checklist

Before pushing to GitHub, verify:

### Student

- [ ] Student signup works
- [ ] Invalid email domain is rejected
- [ ] Hostel is saved
- [ ] Student login works
- [ ] Forgot password works
- [ ] Complaint submission works
- [ ] Student sees only own complaints
- [ ] Complaint history works

### Warden

- [ ] H1 warden sees H1 complaints
- [ ] H1 warden does not see H2 complaints
- [ ] Warden can assign maintenance staff
- [ ] Warden can move complaint to In Progress
- [ ] Resolution note is required for Resolved
- [ ] Warden cannot reject complaints
- [ ] Warden sees hostel-specific dashboard statistics

### Administrator

- [ ] Admin can see all complaints
- [ ] Admin can view student directory
- [ ] Student hostel appears in directory
- [ ] Admin can view warden assignments
- [ ] H1-H14 assignments are displayed
- [ ] Admin can reject a complaint

---

# GitHub Notes

Do not commit the following:

```text
venv/
database.db
__pycache__/
*.pyc
.env
```

A basic `.gitignore` can contain:

```gitignore
venv/
__pycache__/
*.pyc
database.db
.env
```

The repository should contain the source code and setup scripts, not your local database.

---

# Current Scope

This project intentionally stays small.

It does not currently include:

- React
- Node.js
- MongoDB
- AI/ML
- Real email delivery
- SMS notifications
- Payment processing
- Mobile application
- Microservices
- Docker-based deployment

The focus is the hostel maintenance workflow, role-based access, and a clean Flask/SQLite implementation.

---

# Possible Future Improvements

Some realistic next additions would be:

- Photo attachment with complaint submission
- Email notification when complaint status changes
- Maintenance staff accounts
- Complaint SLA tracking
- Monthly hostel maintenance reports
- Export complaints to CSV/PDF
- PostgreSQL for production deployment
- Deployment with Gunicorn and Nginx
- Audit logs for administrative actions

---

# License

This project is intended for educational and portfolio use.

