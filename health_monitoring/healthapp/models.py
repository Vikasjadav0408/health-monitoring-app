from django.contrib.auth.models import AbstractUser
from django.db import models
from typing import TYPE_CHECKING

# Create your models here.

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    # Add more common fields if needed

if TYPE_CHECKING:
    from .models import User

class PatientProfile(models.Model):
    user: 'User' = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    # Add patient-specific fields here (e.g., age, gender, etc.)
    def __str__(self):
        return self.user.username  # type: ignore

class DoctorProfile(models.Model):
    user: 'User' = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    # Add doctor-specific fields here (e.g., specialization, license number, etc.)
    def __str__(self):
        return self.user.username  # type: ignore

class HealthData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_data')
    date = models.DateTimeField(auto_now_add=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)  # bpm
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)  # mmHg
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)  # mmHg
    blood_sugar = models.FloatField(null=True, blank=True)  # mg/dL
    temperature = models.FloatField(null=True, blank=True)  # Celsius
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-date']

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.username} - {self.doctor.username} on {self.appointment_date}"
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
