"""
MongoDB JSON Schema definitions for collections
"""

EMPLOYEE_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["employee_id", "name", "department", "salary", "joining_date"],
        "properties": {
            "employee_id": {
                "bsonType": "string",
                "pattern": "^E[0-9]{3}$",
                "description": "Employee ID must be in format E123 (E followed by 3 digits)"
            },
            "name": {
                "bsonType": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "Employee name is required and must be between 1-100 characters"
            },
            "department": {
                "bsonType": "string",
                "enum": ["Engineering", "HR", "Marketing", "Finance", "Operations", "Sales"],
                "description": "Department must be one of the predefined values"
            },
            "salary": {
                "bsonType": "int",
                "minimum": 0,
                "maximum": 1000000,
                "description": "Salary must be a positive integer between 0 and 1,000,000"
            },
            "joining_date": {
                "bsonType": ["date", "string"],
                "description": "Joining date must be a valid date or date string"
            },
            "skills": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "minLength": 1,
                    "maxLength": 50
                },
                "uniqueItems": True,
                "description": "Skills must be an array of unique strings, each 1-50 characters"
            },
            "id": {
                "bsonType": "int",
                "description": "Django auto-generated ID field"
            }
        },
        "additionalProperties": True  # Allow MongoDB _id and other fields
    }
}

# Schema for user collection (if needed)
USER_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["username", "email"],
        "properties": {
            "username": {
                "bsonType": "string",
                "minLength": 3,
                "maxLength": 30,
                "pattern": "^[a-zA-Z0-9_]+$",
                "description": "Username must be 3-30 characters, alphanumeric and underscores only"
            },
            "email": {
                "bsonType": "string",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "description": "Must be a valid email address"
            },
            "first_name": {
                "bsonType": "string",
                "maxLength": 50,
                "description": "First name maximum 50 characters"
            },
            "last_name": {
                "bsonType": "string",
                "maxLength": 50,
                "description": "Last name maximum 50 characters"
            },
            "is_active": {
                "bsonType": "bool",
                "description": "User active status"
            },
            "date_joined": {
                "bsonType": "date",
                "description": "Date when user joined"
            }
        },
        "additionalProperties": True
    }
}