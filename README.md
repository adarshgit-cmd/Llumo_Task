# Employee Management System API

A Django REST API for managing employee data with MongoDB backend, JWT authentication, pagination, and schema validation.

## 🚀 Features

- **Employee CRUD Operations** with MongoDB storage
- **JWT Authentication** for secure API access
- **Advanced Search & Filtering** by department and skills
- **Pagination** with metadata for large datasets
- **MongoDB Aggregation** for analytics (average salary by department)
- **JSON Schema Validation** for data integrity
- **MongoDB Indexing** for optimized performance

## 📋 Requirements

- Python 3.8+
- MongoDB 4.0+
- Django 3.1.12
- Django REST Framework 3.14.0

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/adarshgit-cmd/Llumo_Task.git
cd Llumo_Task
```

### 2. Create Virtual Environment
```bash
python -m venv .llumo_venv
# Windows
.llumo_venv\Scripts\activate
# macOS/Linux
source .llumo_venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
MONGO_URI=mongodb://localhost:27017/
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Database Setup
```bash
cd llumo
python manage.py migrate
```

### 6. Create MongoDB Indexes (Optional but Recommended)
```bash
python manage.py create_indexes
```

### 7. Apply Schema Validation
```bash
python manage.py apply_schema_validation --collection=employees
```

### 8. Run the Server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 🔐 Authentication

### Register a New User
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```

### Login to Get JWT Tokens
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Access Token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
    "refresh": "your-refresh-token-here"
}
```

### Access Protected Endpoints
Include the JWT token in all subsequent requests:
```http
Authorization: Bearer your-access-token-here
```

## 📚 API Endpoints

### User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | ❌ |
| POST | `/api/auth/login/` | Login user | ❌ |
| POST | `/api/auth/refresh/` | Refresh token | ❌ |
| GET | `/api/auth/profile/` | Get user profile | ✅ |
| PUT | `/api/auth/profile/` | Update user profile | ✅ |

### Employee Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/employees/` | List all employees (paginated) | ✅ |
| POST | `/api/employees/` | Create new employee | ✅ |
| GET | `/api/employees/{employee_id}/` | Get specific employee | ✅ |
| PUT | `/api/employees/{employee_id}/` | Update employee | ✅ |
| DELETE | `/api/employees/{employee_id}/` | Delete employee | ✅ |
| GET | `/api/employees/search/` | Search employees by skill | ✅ |
| GET | `/api/employees/avg-salary/` | Get average salary by department | ✅ |

## 📖 Detailed Usage Examples

### 1. Create Employee
```http
POST /api/employees/
Authorization: Bearer your-access-token
Content-Type: application/json

{
    "employee_id": "E123",
    "name": "John Doe",
    "department": "Engineering",
    "salary": 75000,
    "joining_date": "2023-01-15",
    "skills": ["Python", "MongoDB", "APIs"]
}
```

### 2. List Employees with Pagination
```http
GET /api/employees/?page=1&page_size=10
Authorization: Bearer your-access-token
```

**Response:**
```json
{
    "results": [
        {
            "employee_id": "E123",
            "name": "John Doe",
            "department": "Engineering",
            "salary": 75000,
            "joining_date": "2023-01-15T00:00:00.000Z",
            "skills": ["Python", "MongoDB", "APIs"]
        }
    ],
    "pagination": {
        "current_page": 1,
        "page_size": 10,
        "total_count": 25,
        "total_pages": 3,
        "has_next": true,
        "has_previous": false
    }
}
```

### 3. Filter Employees by Department
```http
GET /api/employees/?department=Engineering&page=1&page_size=5
Authorization: Bearer your-access-token
```

### 4. Search Employees by Skill
```http
GET /api/employees/search/?skill=Python
Authorization: Bearer your-access-token
```

### 5. Get Average Salary by Department
```http
GET /api/employees/avg-salary/
Authorization: Bearer your-access-token
```

**Response:**
```json
[
    {
        "department": "Engineering",
        "avg_salary": 80000
    },
    {
        "department": "HR", 
        "avg_salary": 60000
    }
]
```

### 6. Update Employee
```http
PUT /api/employees/E123/
Authorization: Bearer your-access-token
Content-Type: application/json

{
    "name": "John Smith",
    "salary": 80000,
    "skills": ["Python", "MongoDB", "APIs", "Docker"]
}
```

### 7. Delete Employee
```http
DELETE /api/employees/E123/
Authorization: Bearer your-access-token
```

## 🔧 Management Commands

### Database Indexing
```bash
# Create MongoDB indexes for better performance
python manage.py create_indexes

```

### Schema Validation
```bash
# Apply schema validation to collections
python manage.py apply_schema_validation --collection=employees
python manage.py apply_schema_validation --collection=all

# Test schema validation
python manage.py test_schema_validation --collection=employees

# Show current validation status
python manage.py show_schema_status
```

## 📊 Data Validation

The system enforces strict data validation at the MongoDB level:

### Employee Schema Constraints
- **employee_id**: Must match pattern `E123` (E + 3 digits)
- **name**: Required, 1-100 characters
- **department**: Must be one of: Engineering, HR, Marketing, Finance, Operations, Sales
- **salary**: Integer between 0 and 1,000,000
- **joining_date**: Valid date format
- **skills**: Array of unique strings, each 1-50 characters

### Required Fields
- employee_id
- name  
- department
- salary
- joining_date

## 🚦 Error Handling

The API provides comprehensive error responses:

```json
{
    "error": "Employee not found"
}
```

```json
{
    "error": "employee_id must be unique"
}
```

```json
{
    "error": "Skill parameter is required."
}
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Validation**: Django's built-in password validators
- **Protected Endpoints**: All employee operations require authentication
- **Schema Validation**: Database-level data validation
- **Input Sanitization**: Automatic through Django REST Framework

## 📈 Performance Optimizations

- **MongoDB Indexes**: Optimized queries on employee_id, department, joining_date, skills
- **Pagination**: Efficient data retrieval for large datasets
- **Aggregation Pipeline**: Optimized salary calculations
- **Connection Pooling**: Efficient database connections

## 🧪 Testing

### Test Schema Validation
```bash
python manage.py test_schema_validation --collection=employees
```

### Test API Endpoints
Use the provided examples above or tools like Postman, curl, or httpie.

## 📁 Project Structure

```
llumo/
├── llumo/
│   ├── settings.py          # Django settings with JWT config
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py
├── employees/
│   ├── models.py           # Employee model
│   ├── serializers.py      # API serializers
│   ├── views.py            # API views with JWT protection
│   ├── urls.py             # Employee URLs
│   ├── auth_views.py       # Authentication views
│   ├── auth_serializers.py # Auth serializers
│   ├── schemas.py          # MongoDB JSON schemas
│   └── management/
│       └── commands/       # Custom management commands
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### JWT Settings
- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 1 day
- **Token Rotation**: Enabled
- **Blacklist After Rotation**: Enabled

### Database Settings
- **Engine**: Djongo (Django-MongoDB connector)
- **Database**: assessment_db
- **Connection**: MongoDB URI from environment

