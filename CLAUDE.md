# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based backend service for a healthcare platform that provides professional work platforms for caregivers in home medical services. The system includes patient family management, appointment scheduling, service packages, personnel management, risk control, and medical collaboration features.

## Technology Stack

- **Web Framework**: Flask 2.3+
- **Database**: MySQL 8.0+ with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended
- **Caching**: Redis
- **Message Queue**: Celery + Redis
- **Deployment**: Docker + Docker Compose

## Project Structure

```
FlaskServer/
├── app/
│   ├── __init__.py          # Application factory and extension initialization
│   ├── config.py            # Configuration settings
│   ├── models/              # Database models
│   │   ├── user.py          # User, Recorder, Doctor models
│   │   ├── patient.py       # Family, Patient models
│   │   ├── appointment.py   # Service packages, subscriptions, appointments
│   │   ├── health_record.py # Health records, medical orders
│   │   └── hospital.py      # Hospital-related models
│   ├── views/               # API endpoints
│   │   ├── auth.py          # Authentication APIs
│   │   ├── patient.py       # Patient management APIs
│   │   ├── appointment.py   # Appointment management APIs
│   │   ├── hospital.py      # Hospital appointment APIs
│   │   └── health.py        # Health record APIs
│   ├── services/            # Business logic services
│   └── utils/               # Utility functions
├── extensions.py            # Flask extension instances
├── run.py                   # Application entry point
├── init_db.py               # Database initialization
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Multi-container setup
└── README.md                # Project documentation
```

## Common Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```bash
# Initialize database
flask init_db
# or
python init_db.py

# Create database tables
python run.py init_db

# Create admin user
python run.py create_admin
```

### Running the Application
```bash
# Development mode
python run.py

# Production mode with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app

# Docker deployment
docker-compose up -d
```

### Database Migrations
```bash
# Initialize migration repository
flask db init

# Create migration script
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

## Testing
```bash
# Run simple tests
python simple_test.py

# Run database tests
python test_db.py
```

## Code Architecture

The application follows a modular architecture with clear separation of concerns:

1. **Models**: Define database schema and relationships using SQLAlchemy
2. **Views**: Implement RESTful API endpoints with proper error handling
3. **Services**: Contain business logic separate from API layer
4. **Utils**: Provide reusable helper functions and decorators

The application factory pattern is used in `app/__init__.py` to create the Flask app with proper extension initialization.

## API Structure

API endpoints are organized by resource:
- `/api/v1/auth/` - Authentication (login, refresh tokens)
- `/api/v1/families/` - Patient family management
- `/api/v1/appointments/` - Appointment scheduling
- `/api/v1/health-records/` - Health record management
- `/api/v1/hospitals/` - Hospital partnership management

All APIs require JWT token authentication except for login and registration endpoints.

## Deployment

The application can be deployed using Docker Compose with three services:
1. `app` - Flask application with Gunicorn
2. `db` - MySQL 8.0 database
3. `redis` - Redis for caching and Celery

Environment variables are used for configuration, with defaults provided in `app/config.py`.

## Key Implementation Details

### Authentication and Authorization
- JWT tokens are used for authentication with access tokens (2h expiry) and refresh tokens (30d expiry)
- Role-based access control with roles: 'recorder', 'admin', 'doctor'
- Passwords are securely hashed using Werkzeug's security utilities

### Database Design
Core tables include:
1. **users** - System user information
2. **recorders** - Recorder detailed information
3. **doctors** - Doctor detailed information
4. **families** - Patient family information
5. **patients** - Patient basic information
6. **service_packages** - Service package definitions
7. **patient_subscriptions** - Patient package subscriptions
8. **appointments** - Home service appointments
9. **health_records** - Health check records
10. **medical_orders** - Doctor medical orders
11. **partner_hospitals** - Partner hospital information
12. **hospital_departments** - Hospital department information
13. **hospital_doctors** - Hospital doctor information
14. **hospital_appointments** - Hospital appointment information

### Error Handling
API responses follow a consistent format:
```json
{
  "code": 200,
  "message": "Success message",
  "data": {}
}
```

Common error codes:
- 200: Success
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 500: Internal server error

### File Uploads
- Supports image, audio, and document uploads
- Files stored in `uploads/` directory with subdirectories for organization
- Maximum file size: 16MB

## Development Workflow

### Adding New API Endpoints
1. Create view file in `app/views/` directory
2. Create service file in `app/services/` directory
3. Create or modify models in `app/models/` directory
4. Register blueprint in `app/__init__.py`

### Database Changes
Use Flask-Migrate for database schema changes:
1. Modify model files in `app/models/`
2. Generate migration: `flask db migrate -m "Description"`
3. Apply migration: `flask db upgrade`

## Testing Approach
- Simple unit tests in `simple_test.py`
- Database integration tests in `test_db.py`
- API interface tests in `testing/` directory
- Tests can be run directly with Python interpreter
- Test database initialization and basic CRUD operations

### API Interface Testing
The project includes comprehensive API interface tests in the `testing/` directory:

1. **Authentication Tests** (`test_auth.py`) - Tests for login, refresh token, and registration endpoints
2. **Patient Management Tests** (`test_patient.py`) - Tests for family and patient management endpoints
3. **Appointment Tests** (`test_appointment.py`) - Tests for appointment scheduling and management endpoints
4. **Hospital Tests** (`test_hospital.py`) - Tests for hospital partnership and appointment endpoints

To run all API tests:
```bash
python testing/run_tests.py
# or
python run_api_tests.py
```

To run individual test modules:
```bash
python testing/test_auth.py
python testing/test_patient.py
python testing/test_appointment.py
python testing/test_hospital.py
# or
python run_api_tests.py testing/test_auth.py
python run_api_tests.py testing/test_patient.py
python run_api_tests.py testing/test_appointment.py
python run_api_tests.py testing/test_hospital.py
```

Test documentation is available in `testing/api_test_documentation.md`.

## Additional Development Notes

### Model Relationships
- User model has one-to-one relationships with Recorder and Doctor models
- Family model has one-to-many relationship with Patient model
- Patient model has one-to-many relationships with HealthRecord, Appointment, and other related models
- All relationships use proper foreign key constraints and cascading where appropriate

### API Response Format
All API responses follow a consistent format with:
- `code`: HTTP status code or application-specific code
- `message`: Human-readable message
- `data`: Actual response data

### Security Considerations
- Passwords are hashed using Werkzeug's security utilities
- JWT tokens are used for authentication with proper expiration
- Role-based access control implemented through decorators
- Input validation on all API endpoints
- SQL injection protection through SQLAlchemy ORM

### Environment Configuration
The application uses environment variables for configuration:
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: JWT secret key
- `REDIS_URL`: Redis connection string
- `UPLOAD_FOLDER`: File upload directory
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL

### CLI Commands
The application provides several useful CLI commands:
- `flask init_db`: Initialize database tables
- `flask drop_db`: Drop all database tables
- `flask create_admin`: Create administrator user
- `flask db`: Database migration commands

### Docker Configuration
The project includes Docker and Docker Compose configurations for easy deployment:
- `Dockerfile`: Application container configuration
- `docker-compose.yml`: Multi-container setup with app, db, and redis services