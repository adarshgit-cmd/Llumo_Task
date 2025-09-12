from djongo import models

class Employee(models.Model):
    employee_id = models.CharField(max_length=5, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    salary = models.IntegerField()
    joining_date = models.DateField()
    skills = models.JSONField(blank=True, default=list)

    class Meta:
        db_table = 'employees'

    def __str__(self):
        return f"{self.employee_id} - {self.name}"
