from django.core.management.base import BaseCommand
from django.db import connection
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from employees.schemas import EMPLOYEE_SCHEMA, USER_SCHEMA


class Command(BaseCommand):
    help = 'Apply MongoDB JSON Schema validation to collections'

    def add_arguments(self, parser):
        parser.add_argument(
            '--collection',
            type=str,
            choices=['employees', 'users', 'all'],
            default='all',
            help='Specify which collection to apply schema validation to'
        )
        parser.add_argument(
            '--validate-existing',
            action='store_true',
            help='Validate existing documents against the schema'
        )

    def handle(self, *args, **options):
        try:
            # Connect to MongoDB
            client = MongoClient(connection.settings_dict['CLIENT']['host'])
            db = client.get_database(connection.settings_dict['NAME'])
            
            collection_choice = options['collection']
            validate_existing = options['validate_existing']
            
            if collection_choice in ['employees', 'all']:
                self.apply_employee_schema(db, validate_existing)
            
            if collection_choice in ['users', 'all']:
                self.apply_user_schema(db, validate_existing)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error applying schema validation: {str(e)}')
            )

    def apply_employee_schema(self, db, validate_existing=False):
        """Apply schema validation to employees collection"""
        try:
            collection_name = 'employees'
            
            # Check if collection exists
            if collection_name not in db.list_collection_names():
                self.stdout.write(
                    self.style.WARNING(f'Collection {collection_name} does not exist yet.')
                )
                return
            
            # Validate existing documents if requested
            if validate_existing:
                self.validate_existing_documents(db[collection_name], EMPLOYEE_SCHEMA, collection_name)
            
            # Apply schema validation
            validation_action = "warn" if validate_existing else "error"
            
            db.command({
                "collMod": collection_name,
                "validator": EMPLOYEE_SCHEMA,
                "validationLevel": "strict",
                "validationAction": validation_action
            })
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully applied schema validation to {collection_name} collection')
            )
            
            # Show schema details
            self.show_schema_info(db[collection_name], collection_name)
            
        except OperationFailure as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to apply schema to employees: {str(e)}')
            )

    def apply_user_schema(self, db, validate_existing=False):
        """Apply schema validation to auth_user collection"""
        try:
            collection_name = 'auth_user'
            
            # Check if collection exists
            if collection_name not in db.list_collection_names():
                self.stdout.write(
                    self.style.WARNING(f'Collection {collection_name} does not exist yet.')
                )
                return
            
            # Validate existing documents if requested
            if validate_existing:
                self.validate_existing_documents(db[collection_name], USER_SCHEMA, collection_name)
            
            # Apply schema validation
            validation_action = "warn" if validate_existing else "error"
            
            db.command({
                "collMod": collection_name,
                "validator": USER_SCHEMA,
                "validationLevel": "strict",
                "validationAction": validation_action
            })
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully applied schema validation to {collection_name} collection')
            )
            
            # Show schema details
            self.show_schema_info(db[collection_name], collection_name)
            
        except OperationFailure as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to apply schema to users: {str(e)}')
            )

    def validate_existing_documents(self, collection, schema, collection_name):
        """Validate existing documents against the schema"""
        self.stdout.write(f"Validating existing documents in {collection_name}...")
        
        # Count total documents
        total_docs = collection.count_documents({})
        
        if total_docs == 0:
            self.stdout.write(
                self.style.WARNING(f'No documents found in {collection_name} collection.')
            )
            return
        
        # Try to find documents that would fail validation
        try:
            # This is a simplified validation - MongoDB will do the full validation
            invalid_count = 0
            sample_invalid = []
            
            for doc in collection.find().limit(100):  # Check first 100 docs
                # Basic checks that we can do in Python
                if collection_name == 'employees':
                    if not self.validate_employee_doc(doc):
                        invalid_count += 1
                        if len(sample_invalid) < 3:
                            sample_invalid.append(doc.get('employee_id', 'Unknown ID'))
            
            if invalid_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'Found {invalid_count} potentially invalid documents in {collection_name}. '
                        f'Sample IDs: {sample_invalid}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'All sampled documents in {collection_name} appear valid.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not validate existing documents: {str(e)}')
            )

    def validate_employee_doc(self, doc):
        """Basic validation for employee document"""
        required_fields = ['employee_id', 'name', 'department', 'salary', 'joining_date']
        
        # Check required fields
        for field in required_fields:
            if field not in doc:
                return False
        
        # Check employee_id format
        employee_id = doc.get('employee_id', '')
        if not isinstance(employee_id, str) or len(employee_id) != 4 or not employee_id.startswith('E'):
            return False
        
        # Check salary is positive
        salary = doc.get('salary')
        if not isinstance(salary, int) or salary < 0:
            return False
        
        return True

    def show_schema_info(self, collection, collection_name):
        """Display schema validation info"""
        try:
            # Get collection options to see validation rules
            db = collection.database
            stats = db.command("listCollections", filter={"name": collection_name})
            
            for collection_info in stats['cursor']['firstBatch']:
                if 'options' in collection_info and 'validator' in collection_info['options']:
                    validator = collection_info['options']['validator']
                    validation_level = collection_info['options'].get('validationLevel', 'strict')
                    validation_action = collection_info['options'].get('validationAction', 'error')
                    
                    self.stdout.write(f"\nSchema validation details for {collection_name}:")
                    self.stdout.write(f"  Validation Level: {validation_level}")
                    self.stdout.write(f"  Validation Action: {validation_action}")
                    
                    if '$jsonSchema' in validator:
                        schema = validator['$jsonSchema']
                        required_fields = schema.get('required', [])
                        properties = schema.get('properties', {})
                        
                        self.stdout.write(f"  Required fields: {', '.join(required_fields)}")
                        self.stdout.write(f"  Total schema properties: {len(properties)}")
                    
                    break
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not retrieve schema info: {str(e)}')
            )