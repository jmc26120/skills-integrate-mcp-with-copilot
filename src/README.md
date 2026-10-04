# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Let students view activities and current participants without an account
- Let authenticated teachers register and unregister students
- Keep teacher credentials in a JSON file with salted PBKDF2 password hashes

## Getting Started

1. Install the application dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Create a teacher account from the repository root. The password is entered
   interactively, must be at least 12 characters, and is stored as a salted hash:

   ```
   python -m src.create_teacher coach
   ```

3. Set a stable session signing secret before starting the server. For production,
   also enable secure cookies when serving over HTTPS:

   ```
   export SESSION_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
   export SESSION_COOKIE_SECURE=true
   ```

4. Run the application from the repository root:

   ```
   uvicorn src.app:app --reload
   ```

5. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

6. Run the API tests (install `requirements-dev.txt` first):

   ```
   python -m unittest discover -s tests -v
   ```

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| GET    | `/auth/session`                                                   | Check whether the current browser has a teacher session             |
| POST   | `/auth/login`                                                      | Sign in a teacher and set a signed, HTTP-only session cookie         |
| POST   | `/auth/logout`                                                     | End the current teacher session                                     |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student registration                                   |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only student unregistration                              |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier for activity participation:
   - Name
   - Grade level

3. **Teachers** - Provisioned locally in `src/teachers.json`, which is excluded from Git:
   - Username
   - Random salt and PBKDF2 password hash (never the raw password)

Each environment must create its own teacher accounts with `python -m src.create_teacher <username>`.

Activity and participant data remain in memory and reset when the server restarts.
