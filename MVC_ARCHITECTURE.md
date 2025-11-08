# MVC Architecture Documentation

## Overview

The Appointment Service follows the **MVC (Model-View-Controller)** architecture pattern for better code organization, maintainability, and separation of concerns.

## Project Structure

```
appointment-service/
├── app.py                      # Main application entry point
├── config.py                   # Configuration settings
├── models/                     # Data models (MVC - Model)
│   ├── __init__.py
│   ├── db.py                  # Shared database instance
│   ├── user.py                # User model
│   └── appointment.py         # Appointment model
├── controllers/                # Request handlers (MVC - Controller)
│   ├── __init__.py
│   ├── auth_controller.py     # Authentication endpoints
│   ├── appointment_controller.py  # Appointment endpoints
│   └── health_controller.py   # Health check endpoints
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py        # Authentication business logic
│   ├── appointment_service.py # Appointment business logic
│   └── external_service.py    # External API integration
├── middleware/                 # Request middleware
│   ├── __init__.py
│   └── auth.py                # JWT authentication middleware
└── requirements.txt            # Python dependencies
```

## Architecture Layers

### 1. Models Layer (Data Layer)
**Location**: `models/`

**Responsibility**: 
- Define database schemas
- Handle data persistence
- Provide data access methods

**Files**:
- `db.py`: Shared SQLAlchemy database instance
- `user.py`: User model for authentication
- `appointment.py`: Appointment model

**Example**:
```python
# models/appointment.py
class Appointment(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    patient_id = db.Column(db.String(36), nullable=False)
    # ... other fields
    
    def to_dict(self):
        return {...}
```

### 2. Services Layer (Business Logic)
**Location**: `services/`

**Responsibility**:
- Implement business rules
- Handle complex logic
- Coordinate between models and external services

**Files**:
- `auth_service.py`: User authentication logic
- `appointment_service.py`: Appointment business rules
- `external_service.py`: External API calls

**Example**:
```python
# services/appointment_service.py
class AppointmentService:
    @staticmethod
    def book_appointment(...):
        # Validate business rules
        # Check availability
        # Create appointment
        return appointment
```

### 3. Controllers Layer (Request Handling)
**Location**: `controllers/`

**Responsibility**:
- Handle HTTP requests
- Validate input
- Call services
- Return HTTP responses

**Files**:
- `auth_controller.py`: Authentication endpoints
- `appointment_controller.py`: Appointment endpoints
- `health_controller.py`: Health check endpoints

**Example**:
```python
# controllers/appointment_controller.py
@appointment_bp.route('', methods=['POST'])
@token_required
def book_appointment(current_user_id, current_user_role):
    # Parse request
    # Call service
    # Return response
    return jsonify({...})
```

### 4. Middleware Layer
**Location**: `middleware/`

**Responsibility**:
- Authentication/Authorization
- Request validation
- Cross-cutting concerns

**Files**:
- `auth.py`: JWT authentication decorators

**Example**:
```python
# middleware/auth.py
@token_required
def protected_endpoint(...):
    # Only accessible with valid JWT token
    pass
```

## Data Flow

```
HTTP Request
    ↓
Controller (Parse request, validate input)
    ↓
Middleware (Authentication, authorization)
    ↓
Service (Business logic, validations)
    ↓
Model (Database operations)
    ↓
Service (Process results)
    ↓
Controller (Format response)
    ↓
HTTP Response
```

## Benefits of MVC Architecture

1. **Separation of Concerns**: Each layer has a clear responsibility
2. **Maintainability**: Easy to locate and modify code
3. **Testability**: Each layer can be tested independently
4. **Scalability**: Easy to add new features without affecting other layers
5. **Reusability**: Services can be reused across multiple controllers

## Key Design Patterns

### 1. Factory Pattern
**Application**: `create_app()` function creates and configures the Flask application

```python
def create_app():
    app = Flask(__name__)
    # Configuration
    # Blueprint registration
    return app
```

### 2. Dependency Injection
**Application**: Database instance is injected into models and services

```python
from models.db import db

class User(db.Model):
    # Uses injected db instance
    pass
```

### 3. Decorator Pattern
**Application**: `@token_required` decorator for authentication

```python
@token_required
def protected_endpoint(...):
    # Protected by authentication
    pass
```

### 4. Service Layer Pattern
**Application**: Business logic separated into service classes

```python
class AppointmentService:
    @staticmethod
    def book_appointment(...):
        # Business logic here
        pass
```

## ORM: SQLAlchemy

**Note**: The project uses **SQLAlchemy** (Python's ORM), which is equivalent to Sequelize in Node.js. SQLAlchemy provides:
- Object-relational mapping
- Database abstraction
- Query building
- Relationship management

## Authentication: JWT

The service uses **JWT (JSON Web Tokens)** for authentication:
- Token-based authentication
- Stateless (no server-side session storage)
- Secure token signing with secret key
- Token expiration support

## Best Practices

1. **Controllers should be thin**: Only handle HTTP concerns
2. **Business logic in services**: Keep controllers simple
3. **Models for data access**: Don't put business logic in models
4. **Use dependency injection**: For better testability
5. **Error handling**: Handle errors at appropriate layers
6. **Validation**: Validate input at controller level
7. **Authorization**: Check permissions in middleware or services

## Testing Strategy

### Unit Tests
- Test services independently
- Mock external dependencies
- Test business logic

### Integration Tests
- Test controllers with services
- Test database operations
- Test authentication flow

### End-to-End Tests
- Test complete request/response cycle
- Test API endpoints
- Test authentication

## Extending the Architecture

### Adding a New Feature

1. **Create Model** (if needed):
   ```python
   # models/new_model.py
   class NewModel(db.Model):
       # Define schema
       pass
   ```

2. **Create Service**:
   ```python
   # services/new_service.py
   class NewService:
       @staticmethod
       def do_something(...):
           # Business logic
           pass
   ```

3. **Create Controller**:
   ```python
   # controllers/new_controller.py
   new_bp = Blueprint('new', __name__)
   
   @new_bp.route('', methods=['POST'])
   @token_required
   def new_endpoint(...):
       # Handle request
       pass
   ```

4. **Register Blueprint**:
   ```python
   # app.py
   app.register_blueprint(new_bp, url_prefix='/api/v1/new')
   ```

## Summary

The MVC architecture provides a clean, maintainable, and scalable structure for the Appointment Service. Each layer has clear responsibilities, making the codebase easy to understand and extend.


