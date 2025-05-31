# task-manager-fastapi

A simple task management API built with FastAPI, SQLAlchemy, and PostgreSQL. This project allows organizations to manage users and tasks efficiently.

## Features

- Organization management (create, list, retrieve)
- User management (create, list, retrieve, filter by organization)
- Task management (CRUD for tasks, assign to users/organizations)
- Password hashing for user security
- Modular code structure with routers and models

## Project Structure

```
app/
  main.py           # FastAPI app entry point
  database.py       # Database connection and session
  utils.py          # Utility functions (e.g., password hashing)
  core/
    oauth2py        #handles tokenization and verification
  models/
    db_models.py    # SQLAlchemy ORM models
    schemas.py      # Pydantic schemas for validation
    config.py       # Settings management
  routers/
    auth.py         # Authentication endpoints
    assign_task.py  # Assigntasks(admin only) Complete_task endpoints(for file uploads and     change of status)
    org.py          # Organization endpoints
    user.py         # User endpoints
    task.py         # Task endpoints
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database
- (Optional) Create a `.env` file for DB credentials

### Installation

1. Clone the repository:
   ```powershell
   git clone <repo-url>
   cd task-manager-fastapi
   ```

2. Install dependencies:
   ```powershell
   pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv passlib[bcrypt] pydantic-settings
   ```

3. Set up your PostgreSQL database and update the connection string in `app/database.py` or use a `.env` file.

### Running the App

Start the FastAPI server:
```powershell
uvicorn app.main:app --reload
```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive API documentation.

## API Endpoints

- `GET /org` - List all organizations
- `POST /org` - Create a new organization
- `GET /org/{org_id}` - Get organization by ID
- `GET /user` - List all users
- `POST /user` - Create a new user
- `GET /user/{user_id}` - Get user by ID
- `GET /user/{org_id}` - List users in an organization
- `GET /assigned/` - List all tasks assigned to the current user
- `POST /assigned/` - Assign a task (admin only)
- `PATCH /assigned/{assignment_id}/status` - Update task status and upload proof of completion

## License

MIT



