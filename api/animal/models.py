from django.db import models
from django.conf import settings


class Animal(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    species = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='animals', on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class AnimalMeasurement(models.Model):
    animal = models.ForeignKey(Animal, related_name='measurements', on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # weight in lbs
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    def __str__(self):
        return f"{self.animal.name} - {self.date}"

class Vaccination(models.Model):
    animal = models.ForeignKey(Animal, related_name='vaccinations', on_delete=models.CASCADE)
    vaccine_name = models.CharField(max_length=100)
    date_administered = models.DateField()
    description = models.TextField(blank=True, null=True)
    next_due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.animal.name} - {self.vaccine_name}"

class AnimalDetail(models.Model):
    animal = models.ForeignKey(Animal, related_name='details', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_recorded = models.DateField()

    def __str__(self):
        return f"{self.animal.name} - {self.date_recorded}"
