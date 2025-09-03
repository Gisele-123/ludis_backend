# Ludis Backend

Ludis is a tech-driven sports ecosystem connecting athletes, fans, sponsors, and federations. This backend is built with **Python Flask**, supporting **user authentication with email verification** and **live match updates**.

---

## Table of Contents

- [Features Implemented](#features-implemented)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Database Migrations](#database-migrations)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Teams & Matches](#teams--matches)
- [Testing the APIs](#testing-the-apis)
- [Admin Credentials](#admin-credentials)

---

## Features Implemented

1. **Auth**
   - User Registration with `first_name`, `last_name`, `email`, `phone`, and `password`
   - Email verification using Gmail SMTP
   - Login with JWT token
   - Get current user info (`/auth/me`)
   - Admin static login

2. **Live Scores & Match Updates**
   - CRUD for Teams (Admin only)
   - CRUD for Matches (Admin only)
   - Public endpoints for listing teams, matches, upcoming/live/finished matches
   - Update match scores and status (Admin only)

---

## Project Structure

```

ludis-backend/
├── app/
│   ├── **init**.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   └── auth/
│       ├── **init**.py
│       ├── routes.py
│       └── utils.py
│   └── matches/
│       ├── **init**.py
│       └── routes.py
├── wsgi.py
├── requirements.txt
└── .env

````

---

## Setup Instructions

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd ludis-backend
````

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Create `.env` file**

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=sqlite:///ludis.db
APP_BASE_URL=http://localhost:5000
CORS_ORIGINS=http://localhost:3000,*
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=your_gmail@gmail.com
```

> **Note:** You need a Gmail App Password for `MAIL_PASSWORD`.

---

## Database Migrations

```bash
# Initialize migrations
python -m flask db init

# Create migration scripts
python -m flask db migrate -m "Initial migration"

# Apply migrations
python -m flask db upgrade
```

---

## Running the Server

```bash
# Set environment variables (PowerShell)
$env:FLASK_APP="wsgi.py"
$env:FLASK_ENV="development"

# Run server
python -m flask run
```

The server will start at `http://localhost:5000`.

---

## API Documentation

### Authentication

| Endpoint             | Method | Body / Params                                   | Description                                            |
| -------------------- | ------ | ----------------------------------------------- | ------------------------------------------------------ |
| `/auth/register`     | POST   | `first_name, last_name, email, phone, password` | Registers a new user and sends email verification link |
| `/auth/verify-email` | GET    | `token` (query param)                           | Verifies the user email                                |
| `/auth/login`        | POST   | `email, password`                               | Logs in user and returns JWT token                     |
| `/auth/me`           | GET    | Header: `Authorization: Bearer <token>`         | Returns logged-in user info                            |

**Admin Login:**

```json
POST /auth/login
{
    "email": "admin@ludis.rw",
    "password": "Ludis123"
}
```

---

### Teams & Matches

**Admin-only routes** (require JWT token of admin):

| Endpoint                      | Method | Body / Params                                                             | Description             |
| ----------------------------- | ------ | ------------------------------------------------------------------------- | ----------------------- |
| `/matches/teams`              | POST   | `{ "name": "Team A" }`                                                    | Create a team           |
| `/matches/matches`            | POST   | `{ "home_team_id": 1, "away_team_id": 2, "date": "2025-09-03T15:00:00" }` | Create a match          |
| `/matches/matches/<id>/score` | PATCH  | `{ "home_score": 1, "away_score": 2, "status": "live" }`                  | Update score and status |

**Public routes**:

| Endpoint                   | Method | Description                                                |
| -------------------------- | ------ | ---------------------------------------------------------- |
| `/matches/teams`           | GET    | List all teams                                             |
| `/matches/teams/<id>`      | GET    | Get single team info                                       |
| `/matches/matches`         | GET    | List all matches                                           |
| `/matches/matches/<id>`    | GET    | Get single match info                                      |
| `/matches/status/<status>` | GET    | Filter matches by status (`scheduled`, `live`, `finished`) |
| `/matches/team/<id>`       | GET    | Filter matches for a specific team                         |

---

## Testing the APIs

1. **Register a user**

```bash
POST http://localhost:5000/auth/register
Body:
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "0781234567",
    "password": "secret123"
}
```

2. **Check your email** → Click verification link

3. **Login**

```bash
POST http://localhost:5000/auth/login
Body:
{
    "email": "john@example.com",
    "password": "secret123"
}
```

> Response contains `access_token`

4. **Get user info**

```bash
GET http://localhost:5000/auth/me
Headers: Authorization: Bearer <access_token>
```

5. **Admin creates teams & matches**

```bash
POST http://localhost:5000/matches/teams
Headers: Authorization: Bearer <ADMIN_TOKEN>
Body: { "name": "Team A" }
```

```bash
POST http://localhost:5000/matches/matches
Headers: Authorization: Bearer <ADMIN_TOKEN>
Body:
{
    "home_team_id": 1,
    "away_team_id": 2,
    "date": "2025-09-03T15:00:00"
}
```

6. **Update live score (Admin only)**

```bash
PATCH http://localhost:5000/matches/matches/1/score
Headers: Authorization: Bearer <ADMIN_TOKEN>
Body: { "home_score": 2, "away_score": 1, "status": "live" }
```

7. **Public fetching of matches & teams**

```bash
GET http://localhost:5000/matches/matches
GET http://localhost:5000/matches/teams
GET http://localhost:5000/matches/status/live
GET http://localhost:5000/matches/team/1
```

---

## Admin Credentials

```
Email: admin@ludis.rw
Password: Ludis123
```

> Only admin can create teams, matches, and update live scores.

---

## Notes

* Frontend can **poll `/matches/matches`** or `/matches/status/live` every few seconds for live updates.
* All JWT-protected routes require the **Authorization header**:

```
Authorization: Bearer <token>
```

* Email verification is required for **regular users** before login.

---