# Personal Finance App

This is a comprehensive personal finance application designed to help users manage their finances, track expenses, and share account access. The application is built with a modern web stack, featuring a Flask backend and a Reflex frontend, all containerized with Docker.

## Key Features

- **User Authentication:** Secure user registration and login, with a password reset feature.
- **Account Management:** Create and manage multiple financial accounts.
- **Transaction Tracking:** Log income and expenses with categories and descriptions.
- **Account Sharing:** Invite other users to access and collaborate on accounts.
- **PSD2 Integration:** Connect to bank accounts for automated transaction syncing (demo).

## Technologies Used

- **Backend:** Flask (Python)
- **Frontend:** Reflex (Python)
- **Database:** PostgreSQL
- **Web Server / Proxy:** Nginx
- **Containerization:** Docker & Docker Compose

## Deployment

The application is deployed and publicly accessible at:

**[https://langa.dev](https://langa.dev)**

## Running the Application Locally

There are two primary ways to run the application: using Docker for a production-like environment or running the services manually for development.

### 1. Production Mode (with Docker)

This is the recommended way to run the application as it handles all services, networking, and dependencies.

**Prerequisites:**
- Docker and Docker Compose must be installed.

**Instructions:**

1.  **Navigate to the project's root directory.**
2.  **Build and start the services:**
    ```bash
    docker-compose up --build
    ```
3.  **Access the application:**
    Open your web browser and navigate to `http://localhost`.

### 2. Development Mode (Manual)

These instructions are for running the backend and frontend services separately, which is useful for development and debugging.

**Prerequisites:**
- Python 3.10+
- A virtual environment tool (like `venv`)

**Instructions:**

1.  **Create and activate a virtual environment:**
    ```powershell
    # Create the virtual environment
    python -m venv .venv

    # Activate the virtual environment
    .\\.venv\\Scripts\\activate
    ```

2.  **Install dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

3.  **Start the Backend (Flask):**
    In a terminal, from the project's root directory:
    ```powershell
    $env:FLASK_APP = "backend.app"
    $env:FLASK_DEBUG = "1"
    flask run
    ```

4.  **Start the Frontend (Reflex):**
    Open a **new terminal** and navigate to the `frontend` directory:
    ```powershell
    cd frontend
    ..\\.venv\\Scripts\\activate
    reflex run
    ```

## Nginx Configuration for SPA

The Nginx service is configured to correctly handle the client-side routing of the Reflex (Single Page Application). It proxies API requests to the backend and serves the frontend application, with a fallback to `index.html` to ensure that routes like `/reset-password/[token]` are handled by the Reflex router.
