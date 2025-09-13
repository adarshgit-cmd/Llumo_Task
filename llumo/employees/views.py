from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
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
