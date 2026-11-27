# ALAGA: Where Compassion Takes Action

ALAGA is a web application for residents of pilot barangays in Cebu City. Residents report stray, sick, lost, or found animals, admins monitor and moderate the reports, and verified responders (a later increment) will help resolve them. It gives the community one place to post, find, and track animal cases that are otherwise scattered across social media and word of mouth.

Course: CSIT327 Information Management, Section G8
Student: Tiro, Careza

## Core Feature: Animal Case Reporting & Tracking

Residents report animals that need help, are lost, or were found. Each case has a type, animal, urgency level, description, map pin, landmark, and 1 to 3 photos. A case is tracked from **open** to **being handled** to **resolved**, and every status change is saved in a history.

What each role can do:

| Role | Abilities |
|---|---|
| Resident | Report an animal, browse My Cases and the community feed (with filters and search), edit or delete their own cases, and update the status of their own cases |
| Admin | View all cases including hidden ones, hide or restore cases, reopen resolved cases, and see case statistics on the dashboard |

Business rules enforced in the code:

- A case needs 1 to 3 valid images of at most 5 MB each
- The map pin must be inside the pilot area (Cebu City)
- A user can post at most 10 cases per day
- Status can only move from open to being handled to resolved, and only the reporter or an admin can change it
- Every status change creates a history record
- Cases are never permanently deleted. Deleting a case hides it.
- Users can only edit or delete their own cases, and resolved cases cannot be edited

## Standard Features

- Registration with validation and hashed passwords
- Login and logout with protected pages
- Role-based dashboards for Resident and Admin
- Profile view and edit

## Tech Stack

- Python and Django 5.2 (backend and frontend through Django templates)
- PostgreSQL on Supabase
- Bootstrap 5 and Leaflet (OpenStreetMap) for the interface and maps
- Pillow for image uploads

## Project Structure

```
alaga/          project settings and root URLs
accounts/       users, barangays, registration, login, profile
dashboard/      role-based dashboards
cases/          core feature: models, forms, views, status rules
templates/      all HTML templates
```

## Setup

Requirements: Python 3.10 or newer, Git, and a Supabase (or PostgreSQL) database.

1. Clone the repository

```
git clone https://github.com/tirocareza7-del/ALAGA-Tiro-Careza-G8.git
cd ALAGA-Tiro-Careza-G8
```

2. Create and activate a virtual environment

```
python -m venv venv
venv\Scripts\activate
```

3. Install the dependencies

```
pip install -r requirements.txt
```

4. Create your `.env` file from the example

```
copy .env.example .env
```

Open `.env` and fill in these values:

| Variable | Description |
|---|---|
| `SECRET_KEY` | A long random string. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `True` for local development |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` |
| `DATABASE_URL` | Your Supabase Session pooler connection string, or a local PostgreSQL URL |

The `.env` file is ignored by Git and must never be committed.

5. Create the database tables and starting data

```
python manage.py migrate
python manage.py seed_barangays
python manage.py createsuperuser
```

When `createsuperuser` asks for the barangay, enter `1`. The superuser is the Admin account.

6. Run the server

```
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## Using the App

1. Register a resident account at `/register/`, or log in with an existing one
2. As a resident, use **Report an Animal** to post a case, then open **My Cases** to track it
3. Log in as the admin to see **All Cases**, hide or restore cases, and view the Admin dashboard

Case photos are saved in the local `media/` folder, which is not stored in Git.

## Test Accounts

| Role | Email | Password |
|---|---|---|
| Admin | provided in the PD2 report | provided in the PD2 report |
| Resident | provided in the PD2 report | provided in the PD2 report |

## Branching

- `main`: stable code only
- `develop`: integration branch
- `feature/<name>`: one branch per feature, merged into `develop` through a pull request

## Known Limitations

- Email/OTP verification is not implemented yet
- Photos are stored locally instead of in Supabase Storage
- The pilot-area check uses a rectangle around Cebu City, not exact barangay boundaries
- A resident cannot undo an accidental status change. An admin must reopen the case.

## Planned Features

Responder verification, messaging, notifications and follow-up emails, health and pest alerts, a vet clinic list, post flagging, an activity log, a map view of all cases, and changing your password from the profile page.
