from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('register/patient/', views.patient_register, name='patient_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    path('dashboard/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('add-health-data/', views.add_health_data, name='add_health_data'),
    path('doctors/', views.list_doctors, name='list_doctors'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('update-appointment/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
]
