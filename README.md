# Personal Finance App

This is a personal finance application built with a Flask backend and a Reflex frontend.

## Technologies Used

- **Backend:** Flask
- **Frontend:** Reflex
- **Database:** PostgreSQL (from `docker/init.sql`)

## Database Schema

The database schema is defined in `docker/init.sql`. It includes the following tables:

- `users`
- `accounts`
- `user_account_access`
- `categories`
- `transactions`
- `account_invitations`

## Running the Application

### Development Mode

These instructions are for running the application in a development environment from the project's root directory.

**1. Start the Backend (Flask):**

Ensure you are in the project's root directory.

```powershell
# Set PowerShell execution policy to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activate the virtual environment
.\\.venv\\Scripts\\activate

# Configure Flask environment variables
$env:FLASK_APP = "backend.app"
$env:FLASK_DEBUG = "1"

# Run the Flask development server
flask run
```

**2. Start the Frontend (Reflex):**

Open a new terminal in the project's root directory.

```powershell
# Navigate to the frontend directory
cd frontend

# Set PowerShell execution policy to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activate the virtual environment (located in the project root)
..\\.venv\\Scripts\\activate

# Run the Reflex development server
reflex run
```
