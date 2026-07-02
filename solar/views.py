from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
import datetime

from .forms import SignupForm, LoginForm, CalculatorForm
from .models import SolarCalculation, Client, SolarPlant, MeterReading, Payment, Notification, Tariff
from .services import calculate_solar_investment

def landing_view(request):
    return render(request, 'solar/landing.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user, backend='solar.authentication.MobileNumberBackend')
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'solar/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            mobile_number = form.cleaned_data.get('mobile_number')
            password = form.cleaned_data.get('password')
            user = authenticate(request, mobile_number=mobile_number, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid mobile number or password.")
    else:
        form = LoginForm()
    return render(request, 'solar/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

from django.shortcuts import get_object_or_404

@login_required(login_url='login')
def dashboard_view(request):
    context = {}
    calc_id = request.GET.get('calc_id')
    
    if calc_id:
        latest_calc = get_object_or_404(SolarCalculation, id=calc_id, user=request.user)
        context['force_show_calc'] = True
    else:
        latest_calc = SolarCalculation.objects.filter(user=request.user).order_by('-created_at').first()
        
    context['latest_calc'] = latest_calc
    
    try:
        client = request.user.client_profile
        context['has_client'] = True
        
        plants = client.plants.all()
        context['project_cost'] = sum(p.project_cost for p in plants)
        context['client_investment'] = sum(p.client_investment for p in plants)
        context['company_investment'] = sum(p.company_investment for p in plants)
        
        today = datetime.date.today()
        todays_gen = 0
        monthly_gen = 0
        own_usage = 0
        monthly_exported_units = 0
        lifetime_gen = 0
        exported_units = 0
        
        gross_revenue = 0
        maintenance = 0
        net_earnings = 0
        payment_status = "No Payments"
        
        yearly_data_dict = {}
        
        for plant in plants:
            readings = plant.readings.all()
            todays_gen += sum(r.daily_generation for r in readings if r.reading_date == today)
            monthly_gen += sum(r.monthly_generation for r in readings if r.reading_date.month == today.month and r.reading_date.year == today.year)
            own_usage += sum(r.self_consumption for r in readings if r.reading_date.month == today.month and r.reading_date.year == today.year)
            monthly_exported_units += sum(r.electricity_exported for r in readings if r.reading_date.month == today.month and r.reading_date.year == today.year)
            
            lifetime_gen += sum(r.lifetime_generation for r in readings)
            exported_units += sum(r.electricity_exported for r in readings)
            
            payments = plant.payments.all()
            for p in payments:
                gross_revenue += p.gross_revenue
                maintenance += p.maintenance_charge
                net_earnings += p.net_earnings
                
                # Year-wise aggregation
                year = p.month.year
                if year not in yearly_data_dict:
                    yearly_data_dict[year] = {
                        'year': year,
                        'profit': 0,
                        'investment': float(plant.total_investment),
                    }
                yearly_data_dict[year]['profit'] += float(p.net_earnings)
                
            latest_payment = payments.order_by('-payment_date').first()
            if latest_payment:
                payment_status = latest_payment.get_payment_status_display()
        
        # Calculate ROI for yearly data
        yearly_data = []
        for year, data in sorted(yearly_data_dict.items(), key=lambda x: x[0], reverse=True):
            if data['investment'] > 0:
                data['roi'] = (data['profit'] / data['investment']) * 100
            else:
                data['roi'] = 0
            yearly_data.append(data)
        
        current_value = context['client_investment'] + net_earnings
        roi = (net_earnings / context['client_investment'] * 100) if context['client_investment'] > 0 else 0
        
        # Baseline variables for interactive projection
        latest_tariff_rate = 0
        latest_maintenance_pct = 0
        latest_tax_pct = 0
        
        if plants:
            latest_payment = Payment.objects.filter(plant__in=plants).order_by('-payment_date').first()
            if latest_payment:
                latest_tariff_rate = float(latest_payment.tariff_rate)
                latest_maintenance_pct = float(latest_payment.maintenance_percentage)
                latest_tax_pct = float(latest_payment.tax_percentage)
            else:
                # Fallback to tariff from plant
                p = plants.first()
                if p and p.tariff:
                    latest_tariff_rate = float(p.tariff.rate_per_kwh)

        context.update({
            'current_project_value': current_value,
            'todays_generation': todays_gen,
            'monthly_generation': monthly_gen,
            'own_usage': own_usage,
            'monthly_exported_units': monthly_exported_units,
            'lifetime_generation': lifetime_gen,
            'electricity_exported': exported_units,
            'gross_revenue': gross_revenue,
            'maintenance_charges': maintenance,
            'net_earnings': net_earnings,
            'roi': roi,
            'payment_status': payment_status,
            'yearly_data': yearly_data,
            'latest_tariff_rate': latest_tariff_rate,
            'latest_maintenance_pct': latest_maintenance_pct,
            'latest_tax_pct': latest_tax_pct,
            'notifications': client.notifications.order_by('-date')[:5]
        })
        
    except Client.DoesNotExist:
        context['has_client'] = False

    return render(request, 'solar/dashboard.html', context)

@login_required(login_url='login')
def dashboard_charts_api_view(request):
    try:
        client = request.user.client_profile
        client_inv = sum(p.client_investment for p in client.plants.all())
        company_inv = sum(p.company_investment for p in client.plants.all())
        
        gross = 0
        maint = 0
        tax = 0
        net = 0
        for plant in client.plants.all():
            for p in plant.payments.all():
                gross += float(p.gross_revenue)
                maint += float(p.maintenance_charge)
                tax += float(p.tax_amount)
                net += float(p.net_earnings)

        data = {
            'monthly_gen': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'data': [1200, 1300, 1500, 1800, 1900, 1850]
            },
            'monthly_revenue': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'data': [5400, 5850, 6750, 8100, 8550, 8325]
            },
            'investment_dist': {
                'labels': ['Client Investment', 'Company Investment'],
                'data': [float(client_inv), float(company_inv)]
            },
            'revenue_dist': {
                'labels': ['Net Earnings', 'Maintenance', 'Tax'],
                'data': [net, maint, tax]
            },
            'export_trend': {
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'data': [35, 40, 42, 38, 45, 50, 48]
            },
            'lifetime_prod': {
                'labels': ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'],
                'data': [1200, 2500, 4000, 5800, 7700, 9550]
            }
        }
        return JsonResponse(data)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client profile not found'}, status=404)

@login_required(login_url='login')
def calculator_view(request):
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            monthly_bill = form.cleaned_data['monthly_bill']
            calc_data = calculate_solar_investment(monthly_bill)
            SolarCalculation.objects.create(
                user=request.user,
                **calc_data
            )
            return redirect('dashboard')
    else:
        form = CalculatorForm()
    return render(request, 'solar/calculator.html', {'form': form})

@login_required(login_url='login')
def history_view(request):
    calculations = SolarCalculation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'solar/history.html', {'calculations': calculations})

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'solar/profile.html')

@login_required(login_url='login')
def delete_calculation_view(request, calc_id):
    if request.method == 'POST':
        calc = get_object_or_404(SolarCalculation, id=calc_id, user=request.user)
        calc.delete()
        messages.success(request, "Calculation deleted successfully.")
    return redirect('history')
