from django.core.management.base import BaseCommand
from django.db import connection
from pymongo import MongoClient
from pymongo.errors import WriteError
import json


class Command(BaseCommand):
    help = 'Test MongoDB schema validation by inserting test documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--collection',
            type=str,
            choices=['employees', 'users'],
            default='employees',
            help='Specify which collection to test'
        )

    def handle(self, *args, **options):
        try:
            # Connect to MongoDB
            client = MongoClient(connection.settings_dict['CLIENT']['host'])
            db = client.get_database(connection.settings_dict['NAME'])
            
            collection_choice = options['collection']
            
            if collection_choice == 'employees':
                self.test_employee_validation(db)
            elif collection_choice == 'users':
                self.test_user_validation(db)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error testing schema validation: {str(e)}')
            )

    def test_employee_validation(self, db):
        """Test employee schema validation"""
        collection = db.employees
        
        self.stdout.write("Testing Employee Schema Validation...")
        self.stdout.write("=" * 50)
        
        # Test 1: Valid document
        from datetime import datetime
        valid_doc = {
            "employee_id": "E999",
            "name": "Test Employee",
            "department": "Engineering",
            "salary": 75000,
            "joining_date": datetime(2023, 1, 15),
            "skills": ["Python", "MongoDB"]
        }
        
        try:
            # Try to insert valid document
            result = collection.insert_one(valid_doc)
            self.stdout.write(
                self.style.SUCCESS("✓ Valid document accepted")
            )
            # Clean up
            collection.delete_one({"_id": result.inserted_id})
        except WriteError as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Valid document rejected: {e}")
            )
        
        # Test 2: Missing required field
        invalid_doc_missing = {
            "employee_id": "E998",
            "name": "Test Employee",
            # Missing department
            "salary": 75000,
            "joining_date": datetime(2023, 1, 15)
        }
        
        try:
            collection.insert_one(invalid_doc_missing)
            self.stdout.write(
                self.style.ERROR("✗ Document with missing required field was accepted (should be rejected)")
            )
        except WriteError as e:
            self.stdout.write(
                self.style.SUCCESS("✓ Document with missing required field correctly rejected")
            )
        
        # Test 3: Invalid employee_id format
        invalid_doc_format = {
            "employee_id": "INVALID",
            "name": "Test Employee",
            "department": "Engineering",
            "salary": 75000,
            "joining_date": datetime(2023, 1, 15)
        }
        
        try:
            collection.insert_one(invalid_doc_format)
            self.stdout.write(
                self.style.ERROR("✗ Document with invalid employee_id format was accepted (should be rejected)")
            )
        except WriteError as e:
            self.stdout.write(
                self.style.SUCCESS("✓ Document with invalid employee_id format correctly rejected")
            )
        
        # Test 4: Invalid department
        invalid_doc_dept = {
            "employee_id": "E997",
            "name": "Test Employee",
            "department": "InvalidDept",
            "salary": 75000,
            "joining_date": datetime(2023, 1, 15)
        }
        
        try:
            collection.insert_one(invalid_doc_dept)
            self.stdout.write(
                self.style.ERROR("✗ Document with invalid department was accepted (should be rejected)")
            )
        except WriteError as e:
            self.stdout.write(
                self.style.SUCCESS("✓ Document with invalid department correctly rejected")
            )
        
        # Test 5: Negative salary
        invalid_doc_salary = {
            "employee_id": "E996",
            "name": "Test Employee",
            "department": "Engineering",
            "salary": -1000,
            "joining_date": datetime(2023, 1, 15)
        }
        
        try:
            collection.insert_one(invalid_doc_salary)
            self.stdout.write(
                self.style.ERROR("✗ Document with negative salary was accepted (should be rejected)")
            )
        except WriteError as e:
            self.stdout.write(
                self.style.SUCCESS("✓ Document with negative salary correctly rejected")
            )

    def test_user_validation(self, db):
        """Test user schema validation"""
        collection = db.auth_user
        
        self.stdout.write("Testing User Schema Validation...")
        self.stdout.write("=" * 50)
        
        # Test valid user document
        valid_user = {
            "username": "testuser123",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "date_joined": "2023-01-15T00:00:00.000Z"
        }
        
        try:
            result = collection.insert_one(valid_user)
            self.stdout.write(
                self.style.SUCCESS("✓ Valid user document accepted")
            )
            # Clean up
            collection.delete_one({"_id": result.inserted_id})
        except WriteError as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Valid user document rejected: {e}")
            )
        
        # Test invalid email
        invalid_user_email = {
            "username": "testuser123",
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            collection.insert_one(invalid_user_email)
            self.stdout.write(
                self.style.ERROR("✗ User with invalid email was accepted (should be rejected)")
            )
        except WriteError as e:
            self.stdout.write(
                self.style.SUCCESS("✓ User with invalid email correctly rejected")
            )