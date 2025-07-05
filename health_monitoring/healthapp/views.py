from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from .models import User, HealthData, Appointment

# Create your views here.

def index(request):
    return render(request, 'healthapp/index.html')

def patient_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'user_type') and user.user_type == 'patient':
            login(request, user)
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid username or password, or not a patient account.')
    return render(request, 'healthapp/patient_login.html')

def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'user_type') and user.user_type == 'doctor':
            login(request, user)
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Invalid username or password, or not a doctor account.')
    return render(request, 'healthapp/doctor_login.html')

def patient_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already registered. Please log in.')
            return redirect('patient_login')
        # Use custom User model and create_user to hash password and set user_type
        UserModel = get_user_model()
        user = UserModel.objects.create_user(username=username, password=password, email=email, user_type='patient')
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('patient_login')
    return render(request, 'healthapp/patient_register.html')

def doctor_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already registered. Please log in.')
            return redirect('doctor_login')
        # Use custom User model and create_user to hash password and set user_type
        UserModel = get_user_model()
        user = UserModel.objects.create_user(username=username, password=password, email=email, user_type='doctor')
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('doctor_login')
    return render(request, 'healthapp/doctor_register.html')

def get_vital_status(value, vital_type):
    """Determine if a vital is normal, low, or high based on medical standards"""
    if value is None:
        return "No data"
    
    ranges = {
        'heart_rate': {'low': 60, 'high': 100, 'unit': 'bpm'},
        'blood_pressure_systolic': {'low': 90, 'high': 140, 'unit': 'mmHg'},
        'blood_pressure_diastolic': {'low': 60, 'high': 90, 'unit': 'mmHg'},
        'blood_sugar': {'low': 70, 'high': 140, 'unit': 'mg/dL'},
        'temperature': {'low': 36.1, 'high': 37.2, 'unit': '°C'},
    }
    
    if vital_type not in ranges:
        return "Unknown"
    
    range_info = ranges[vital_type]
    if value < range_info['low']:
        return f"Low ({value} {range_info['unit']})"
    elif value > range_info['high']:
        return f"High ({value} {range_info['unit']})"
    else:
        return f"Normal ({value} {range_info['unit']})"

def patient_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('patient_login')
    
    # Get the latest health data for the current user
    latest_health = HealthData.objects.filter(user=request.user).first()
    recent_activity = HealthData.objects.filter(user=request.user)[:5]
    
    # Get patient's appointments
    patient_appointments = Appointment.objects.filter(patient=request.user)[:5]
    
    # Get status for each vital
    vital_status = {}
    if latest_health:
        vital_status = {
            'heart_rate': get_vital_status(latest_health.heart_rate, 'heart_rate'),
            'blood_pressure': get_vital_status(latest_health.blood_pressure_systolic, 'blood_pressure_systolic') if latest_health.blood_pressure_systolic else "No data",
            'blood_sugar': get_vital_status(latest_health.blood_sugar, 'blood_sugar'),
            'temperature': get_vital_status(latest_health.temperature, 'temperature'),
        }
    
    context = {
        'latest_health': latest_health,
        'recent_activity': recent_activity,
        'vital_status': vital_status,
        'patient_appointments': patient_appointments,
    }
    return render(request, 'healthapp/patient_dashboard.html', context)

def add_health_data(request):
    if not request.user.is_authenticated:
        return redirect('patient_login')
    
    if request.method == 'POST':
        heart_rate = request.POST.get('heart_rate')
        blood_pressure_systolic = request.POST.get('blood_pressure_systolic')
        blood_pressure_diastolic = request.POST.get('blood_pressure_diastolic')
        blood_sugar = request.POST.get('blood_sugar')
        temperature = request.POST.get('temperature')
        notes = request.POST.get('notes')
        
        # Create new health data entry
        health_data = HealthData.objects.create(
            user=request.user,
            heart_rate=heart_rate if heart_rate else None,
            blood_pressure_systolic=blood_pressure_systolic if blood_pressure_systolic else None,
            blood_pressure_diastolic=blood_pressure_diastolic if blood_pressure_diastolic else None,
            blood_sugar=blood_sugar if blood_sugar else None,
            temperature=temperature if temperature else None,
            notes=notes
        )
        
        messages.success(request, 'Health data added successfully!')
        return redirect('patient_dashboard')
    
    return render(request, 'healthapp/add_health_data.html')

def list_doctors(request):
    if not request.user.is_authenticated:
        return redirect('patient_login')
    
    # Get all registered doctors
    doctors = User.objects.filter(user_type='doctor')
    return render(request, 'healthapp/list_doctors.html', {'doctors': doctors})

def book_appointment(request, doctor_id):
    if not request.user.is_authenticated:
        return redirect('patient_login')
    
    if request.method == 'POST':
        doctor = User.objects.get(id=doctor_id, user_type='doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        notes = request.POST.get('notes')
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes
        )
        
        messages.success(request, f'Appointment booked successfully with Dr. {doctor.username}!')
        return redirect('patient_dashboard')
    
    doctor = User.objects.get(id=doctor_id, user_type='doctor')
    return render(request, 'healthapp/book_appointment.html', {'doctor': doctor})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')

def doctor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('doctor_login')
    
    # Get appointments for this doctor
    appointments = Appointment.objects.filter(doctor=request.user)[:10]
    
    context = {
        'appointments': appointments,
    }
    return render(request, 'healthapp/doctor_dashboard.html', context)

def update_appointment_status(request, appointment_id):
    if not request.user.is_authenticated or request.user.user_type != 'doctor':
        return redirect('doctor_login')
    
    if request.method == 'POST':
        appointment = Appointment.objects.get(id=appointment_id, doctor=request.user)
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'cancelled', 'completed']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {new_status}.')
        return redirect('doctor_dashboard')
    
    return redirect('doctor_dashboard')
