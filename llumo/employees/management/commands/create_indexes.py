from django.core.management.base import BaseCommand
from django.db import connection
from pymongo import MongoClient


class Command(BaseCommand):
    help = 'Create MongoDB indexes for better performance'

    def handle(self, *args, **options):
        try:
            # Connect to MongoDB
            client = MongoClient(connection.settings_dict['CLIENT']['host'])
            db = client.get_database(connection.settings_dict['NAME'])
            collection = db.employees
            
            # Create index on employee_id
            collection.create_index("employee_id", unique=True)
            self.stdout.write(
                self.style.SUCCESS('Successfully created unique index on employee_id')
            )
            
            # Create index on department for better filtering performance
            collection.create_index("department")
            self.stdout.write(
                self.style.SUCCESS('Successfully created index on department')
            )
            
            # Create index on joining_date for better sorting performance
            collection.create_index("joining_date")
            self.stdout.write(
                self.style.SUCCESS('Successfully created index on joining_date')
            )
            
            # Create index on skills for better search performance
            collection.create_index("skills")
            self.stdout.write(
                self.style.SUCCESS('Successfully created index on skills')
            )
            
            # List all indexes
            indexes = list(collection.list_indexes())
            self.stdout.write(f"\nCurrent indexes on employees collection:")
            for index in indexes:
                self.stdout.write(f"- {index['name']}: {index.get('key', {})}")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating indexes: {str(e)}')
            )




            