from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import connection
from pymongo import MongoClient

class EmployeeViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        skill = request.query_params.get('skill')
        if not skill:
            return Response({'error': 'Skill parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        client = MongoClient(connection.settings_dict['CLIENT']['host'])
        db = client.get_database(connection.settings_dict['NAME'])
        
        # Mongo query: check if skill exists in skills array
        employees = list(db.employees.find({"skills": skill}))
        # Convert ObjectId to string for JSON serialization
        for emp in employees:
            emp['_id'] = str(emp['_id'])

        return Response(employees)

        
    @action(detail=False, methods=['get'], url_path='avg-salary')
    def avg_salary(self, request):
        from django.db import connection
        # Using Djongo, but aggregation via MongoDB driver
        from pymongo import MongoClient
        client = MongoClient(connection.settings_dict['CLIENT']['host'])
        db = client.get_database(connection.settings_dict['NAME'])
        pipeline = [
            {
                '$group': {
                    '_id': '$department',
                    'avg_salary': {'$avg': '$salary'}
                }
            }
        ]
        result = list(db.employees.aggregate(pipeline))
        output = [
            {
                'department': r['_id'],
                'avg_salary': int(r['avg_salary'])
            } for r in result
        ]
        return Response(output)
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'employee_id'

    def list(self, request, *args, **kwargs):
        department = request.query_params.get('department')
        
        client = MongoClient(connection.settings_dict['CLIENT']['host'])
        db = client.get_database(connection.settings_dict['NAME'])
        
        if department:
            # Use MongoDB query for department filtering
            employees = list(db.employees.find({"department": department}).sort("joining_date", -1))
        else:
            # Return all employees, sorted by joining_date (newest first)
            employees = list(db.employees.find({}).sort("joining_date", -1))
        
        # Convert ObjectId to string and format dates for JSON serialization
        for emp in employees:
            emp['_id'] = str(emp['_id'])
            if 'joining_date' in emp and '$date' in str(emp['joining_date']):
                emp['joining_date'] = emp['joining_date']
        
        return Response(employees)
    lookup_field = 'employee_id'

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            return Response({'error': 'employee_id must be unique'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

        def retrieve(self, request, employee_id=None):
            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data)

        def update(self, request, employee_id=None):
            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = EmployeeSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, employee_id=None):
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        employee.delete()
        return Response({'success': 'Employee deleted successfully'}, status=status.HTTP_200_OK)
