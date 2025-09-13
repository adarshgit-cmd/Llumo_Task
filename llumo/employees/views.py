from rest_framework import viewsets
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            return Response({'error': 'employee_id must be unique'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path=r'(?P<employee_id>[^/.]+)')
    def get_by_id(self, request, employee_id=None):
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
