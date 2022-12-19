from django.db import models

# Create your models here.
# Name,Control,Nom,Meas,Tol,Dev,Test,Out Tol
#A5 distance,Y Distance,95.000,120.007,±2.000,25.007,Fail,23.007
class Measurements(models.Model):
    TEST_CHOICES = (
        ('Fail', 'Fail'),
        ('Pass', 'Pass'),
    )

    part_id = models.CharField(max_length=30)
    part_name = models.CharField(max_length=100)
    length_units = models.CharField(max_length=50, null=True)
    control = models.CharField(max_length=100, null=True)
    nom = models.FloatField(null=True)
    measurement = models.FloatField(null=True)
    tolerance = models.FloatField(null=True)
    deviation = models.FloatField(null=True)
    test_result = models.CharField(max_length=10, choices=TEST_CHOICES, null=True)
    out_of_tolerance = models.FloatField(null=True)
    upload_time = models.DateTimeField(null=True)

    def get_fields(self):
        return [(field.name, getattr(self,field.name)) for field in Measurements._meta.fields]

class Part(models.Model):
    part_id = models.CharField(max_length=30, primary_key=True)
    excel_file = models.FileField(upload_to='documents/')
    upload_time = models.DateTimeField(auto_now_add=True)


