from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import connection
from pymongo import MongoClient

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'employee_id'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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

    def list(self, request, *args, **kwargs):
        department = request.query_params.get('department')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        # Calculate skip value for pagination
        skip = (page - 1) * page_size
        
        client = MongoClient(connection.settings_dict['CLIENT']['host'])
        db = client.get_database(connection.settings_dict['NAME'])
        
        # Build query
        query = {}
        if department:
            query["department"] = department
        
        # Get total count for pagination metadata
        total_count = db.employees.count_documents(query)
        
        # Get paginated employees
        employees = list(db.employees.find(query)
                        .sort("joining_date", -1)
                        .skip(skip)
                        .limit(page_size))
        
        # Convert ObjectId to string for JSON serialization
        for emp in employees:
            emp['_id'] = str(emp['_id'])
            if 'joining_date' in emp and '$date' in str(emp['joining_date']):
                emp['joining_date'] = emp['joining_date']
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        response_data = {
            'results': employees,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_previous': has_previous
            }
        }
        
        return Response(response_data)

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
