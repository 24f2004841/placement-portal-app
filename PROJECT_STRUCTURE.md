# Placement Portal App — Project Structure

## Overview
This is a Flask-based placement portal for three roles:
- **Admin**: approves companies and drives, manages users and applications
- **Company**: registers, creates drives, and reviews student applications
- **Student**: registers, browses drives, applies, and tracks application history

The app is server-rendered with **Jinja2 templates** and uses **SQLite** through **Flask-SQLAlchemy**.

## High-level flow
1. `app.py` creates the Flask app and registers the blueprints.
2. `models.py` defines the database schema and relationships.
3. `routes/` contains the role-based request handlers.
4. `templates/` contains the HTML views rendered by each route.
5. `assets/` stores static files served by Flask.

## Dependencies
From `requirements.txt`:
- **Flask**: web framework and routing
- **Flask-Login**: session handling, user loader, `login_required`, `current_user`
- **Flask-SQLAlchemy**: database integration and ORM setup
- **SQLAlchemy**: query helpers and relationship layer
- **Werkzeug**: password helpers (`generate_password_hash`, `check_password_hash`)
- **Jinja2**: template rendering
- **click / blinker / itsdangerous / MarkupSafe / Werkzeug**: Flask runtime dependencies

## Core application files

### `app.py`
- Creates the Flask app with `assets` as the static folder.
- Configures the SQLite database: `sqlite:///database.sqlite3`.
- Initializes `db` and `LoginManager`.
- Registers blueprints:
  - `admin_routes`
  - `student_routes`
  - `company`
- Defines the landing page route `/`.
- Creates a default admin user on first run.

### `models.py`
Defines the application data model:
- `User`: shared login/account table with `role` and `status`
- `Student`: student profile linked 1:1 to `User`
- `Company`: company profile linked 1:1 to `User`
- `Drive`: placement drive posted by a company
- `Application`: student application for a drive

Important relationships:
- `User -> Student` and `User -> Company`: one-to-one
- `Company -> Drive`: one-to-many
- `Student -> Application`: one-to-many
- `Drive -> Application`: one-to-many

## Route modules / services

### `routes/admin.py`
Admin-only workflows:
- login/logout
- dashboard and search
- view all students
- view job applications
- approve/reject applications
- view pending companies
- approve/reject companies
- approve/reject/delete drives
- blacklist users

This is the control center for moderation and approval actions.

### `routes/company.py`
Company workflows:
- register/login
- dashboard with active/pending/closed drives
- create a new drive
- view drive applications
- inspect a single application
- update application status
- close a drive

This module manages the company side of recruitment.

### `routes/student.py`
Student workflows:
- register/login
- dashboard with active companies and applied drives
- edit profile
- browse drives for a company
- view drive details
- apply to a drive
- view application history
- logout

This module is the student-facing entry point for browsing and applying.

## Templates
`templates/` is organized by feature:
- `base.html`: shared layout, Bootstrap, flash message area
- `index.html`: home page with role-based entry links
- `error.html`: reusable error screen
- `login/`: login forms for admin, student, company
- `register/`: signup forms for student, company
- `admin/`: admin dashboard and moderation views
- `student/`: student dashboard, drives, profile, history
- `company/`: company dashboard, drive, application views

These templates are rendered directly by the route handlers; there is no frontend SPA.

## Static assets
`assets/` currently contains:
- `student.png`
- `student.svg`

The app serves this folder as static content.

## API / endpoint map
There are no external API integrations in this project. The “API” surface is the set of Flask routes:

### Public entry points
- `/` — home page
- `/admin_login`
- `/student_register`
- `/student_login`
- `/company_register`
- `/company_login`

### Student endpoints
- `/dashboard`
- `/student/edit_profile/<stu_id>`
- `/student/<com_id>/drives`
- `/student/drive/<drive_id>`
- `/student/apply/<drive_id>`
- `/student/history`
- `/logout`

### Company endpoints
- `/company_dashboard`
- `/company/drive/<drive_no>`
- `/company/drive/<drive_id>/application`
- `/company/update_application/<application_id>`
- `/company/new_drive`
- `/company/drive/<drive_no>` (the file also defines a second handler with the same route pattern)

### Admin endpoints
- `/admin_dashboard`
- `/all_students`
- `/job_applications`
- `/approve_job_application/<app_id>`
- `/reject_job_application/<app_id>`
- `/pending_companies`
- `/approve_company/<user_id>`
- `/reject_company/<user_id>`
- `/all_drives`
- `/approve_drive/<drive_id>`
- `/reject_drive/<drive_id>`
- `/delete_drive/<drive_id>`
- `/blacklist/<user_id>`

## Mental model
The app is a classic server-rendered CRUD system:
- **Users** authenticate through Flask-Login.
- **Roles** decide which blueprint and template set they use.
- **Database models** represent accounts, profiles, drives, and applications.
- **Admins** act as the approval layer between company registration and active drive posting.
- **Students** consume active company/drive data and create applications.
- **Companies** create drives and update application outcomes.

The application is mostly connected through:
- blueprint registration in `app.py`
- model relationships in `models.py`
- route-to-template rendering in `routes/`
- shared UI shell in `templates/base.html`

## Notes
- The app uses plain form submissions and server-side redirects, not a REST or JSON API.
- Authentication is handled with Flask-Login, but password handling is inconsistent across routes (some compare raw values while others import hashing helpers).
- Some route names and handlers are duplicated or loosely coupled, so the project is best understood as a role-based portal rather than a layered service architecture.
