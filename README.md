<<<<<<< HEAD
# Full-Backend-App-using-Fast-Api
=======
# Simple FastAPI Backend

This is a simple backend application using FastAPI, SQLAlchemy, SQLite, JWT authentication, and role-based authorization.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Open:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

## Main Endpoints

- `POST /auth/register` - create a user
- `POST /auth/login` - login and get an access token
- `GET /users/me` - get logged-in user
- `GET /users` - admin-only user list
- `GET /admin/dashboard` - admin-only example route

## Default Roles

Registration supports two roles:

- `user`
- `admin`

For learning purposes, the register endpoint accepts the role directly. In a real app, do not let public users create admin accounts.
>>>>>>> 9f487d3 (Initial Commit)
