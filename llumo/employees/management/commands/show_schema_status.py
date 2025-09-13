from django.core.management.base import BaseCommand
from django.db import connection
from pymongo import MongoClient
import json


class Command(BaseCommand):
    help = 'Show current MongoDB schema validation status for collections'

    def handle(self, *args, **options):
        try:
            # Connect to MongoDB
            client = MongoClient(connection.settings_dict['CLIENT']['host'])
            db = client.get_database(connection.settings_dict['NAME'])
            
            self.stdout.write("MongoDB Schema Validation Status")
            self.stdout.write("=" * 50)
            
            # Get all collections
            collections = db.list_collection_names()
            
            for collection_name in collections:
                self.show_collection_validation(db, collection_name)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking schema validation: {str(e)}')
            )

    def show_collection_validation(self, db, collection_name):
        """Show validation status for a specific collection"""
        try:
            # Get collection options
            stats = db.command("listCollections", filter={"name": collection_name})
            
            for collection_info in stats['cursor']['firstBatch']:
                options = collection_info.get('options', {})
                
                self.stdout.write(f"\nCollection: {collection_name}")
                self.stdout.write("-" * 30)
                
                if 'validator' in options:
                    validator = options['validator']
                    validation_level = options.get('validationLevel', 'strict')
                    validation_action = options.get('validationAction', 'error')
                    
                    self.stdout.write(f"  Status: Schema validation ENABLED")
                    self.stdout.write(f"  Validation Level: {validation_level}")
                    self.stdout.write(f"  Validation Action: {validation_action}")
                    
                    if '$jsonSchema' in validator:
                        schema = validator['$jsonSchema']
                        required_fields = schema.get('required', [])
                        properties = schema.get('properties', {})
                        
                        self.stdout.write(f"  Required fields: {', '.join(required_fields) if required_fields else 'None'}")
                        self.stdout.write(f"  Schema properties: {len(properties)}")
                        
                        # Show property details
                        if properties:
                            self.stdout.write("  Field validations:")
                            for field_name, field_schema in properties.items():
                                field_type = field_schema.get('bsonType', 'any')
                                if isinstance(field_type, list):
                                    field_type = ' | '.join(field_type)
                                
                                constraints = []
                                if 'pattern' in field_schema:
                                    constraints.append(f"pattern: {field_schema['pattern']}")
                                if 'enum' in field_schema:
                                    constraints.append(f"enum: {field_schema['enum']}")
                                if 'minimum' in field_schema:
                                    constraints.append(f"min: {field_schema['minimum']}")
                                if 'maximum' in field_schema:
                                    constraints.append(f"max: {field_schema['maximum']}")
                                if 'minLength' in field_schema:
                                    constraints.append(f"minLen: {field_schema['minLength']}")
                                if 'maxLength' in field_schema:
                                    constraints.append(f"maxLen: {field_schema['maxLength']}")
                                
                                constraint_str = f" ({', '.join(constraints)})" if constraints else ""
                                self.stdout.write(f"    • {field_name}: {field_type}{constraint_str}")
                else:
                    self.stdout.write(f"  Status: No schema validation")
                
                break  # We found our collection
                
        except Exception as e:
            self.stdout.write(f"  Error checking {collection_name}: {str(e)}")