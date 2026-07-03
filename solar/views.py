from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
import datetime
import json

from django.shortcuts import get_object_or_404

from .forms import SignupForm, LoginForm, CalculatorForm
from .models import SolarCalculation, Client, SolarPlant, MeterReading, Payment, Notification, Tariff
from .services import calculate_solar_investment

def landing_view(request):
    return render(request, 'solar/landing.html')

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.conf import settings
from .models import CustomUser

def password_reset_request_view(request):
    initial = {}
    mobile = request.GET.get('mobile')
    print(' Mobile number from GET parameter:', mobile)
    if mobile:
        try:
            user = CustomUser.objects.get(mobile_number=mobile)
            initial['email'] = user.email
            print(' User found for mobile number:', user.email)
        except CustomUser.DoesNotExist:
            print(' No user found for mobile number:', mobile)
            pass
            
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                email_template_name='registration/password_reset_email.html',
                subject_template_name='registration/password_reset_subject.txt',
            )
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm(initial=initial)
        
    return render(request, 'registration/password_reset_form.html', {'form': form})

def password_reset_done_view(request):
    return render(request, 'registration/password_reset_done.html')

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        validlink = True
    else:
        form = None
        validlink = False
        
    return render(request, 'registration/password_reset_confirm.html', {
        'form': form,
        'validlink': validlink,
    })

def password_reset_complete_view(request):
    return render(request, 'registration/password_reset_complete.html')

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


@login_required(login_url='login')
def dashboard_view(request):
    context = {}
    context['project_cost'] = 0
    context['client_investment'] = 0
    context['company_investment'] = 0
    monthly_gen = 0
    own_usage = 0
    latest_tariff_rate = 0
    latest_maintenance_val = 0
    latest_tax_pct = 0
    
    current_value = 0
    todays_gen = 0
    monthly_exported_units = 0
    lifetime_gen = 0
    exported_units = 0
    gross_revenue = 0
    maintenance = 0
    net_earnings = 0
    payment_status = "No Payments"
    yearly_data = []
    roi = 0
    plants = []
    client = None
    
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
        latest_maintenance_val = 0
        latest_tax_pct = 0
        
        if plants:
            latest_payment = Payment.objects.filter(plant__in=plants).order_by('-payment_date').first()
            if latest_payment:
                latest_tariff_rate = float(latest_payment.tariff_rate)
                latest_maintenance_val = float(latest_payment.maintenance_charge)
                latest_tax_pct = float(latest_payment.tax_percentage)
            else:
                # Fallback to tariff from plant
                p = plants.first()
                if p and p.tariff:
                    latest_tariff_rate = float(p.tariff.rate_per_kwh)

    except Client.DoesNotExist:
        context['has_client'] = False
        
    finally:
        # Simulator Logic
        import math
        
        # Determine defaults from latest_calc if available
        def_proj_cost = context['project_cost'] or 500000
        def_monthly_gen = monthly_gen or 1000
        def_own_usage = own_usage or 200
        def_tariff = latest_tariff_rate or 2.25
        def_maint = latest_maintenance_val or 500.0
        def_tax = latest_tax_pct or 0.0

        if latest_calc:
            if latest_calc.sim_project_cost is not None:
                def_proj_cost = latest_calc.sim_project_cost
                def_monthly_gen = latest_calc.sim_monthly_gen
                def_own_usage = latest_calc.sim_own_usage
                def_tariff = latest_calc.sim_tariff_rate
                def_maint = latest_calc.sim_maint_val
                def_tax = latest_calc.sim_tax_pct
            else:
                # Old calculation record fallback
                def_proj_cost = latest_calc.investment

        def safe_float(val, default):
            try:
                if val is None or str(val).strip() == '':
                    return float(default) if default is not None else 0.0
                return float(val)
            except (ValueError, TypeError):
                return float(default) if default is not None else 0.0

        sim_project_cost = safe_float(request.GET.get('project_cost'), def_proj_cost)
        sim_monthly_gen = safe_float(request.GET.get('monthly_gen'), def_monthly_gen)
        sim_own_usage = safe_float(request.GET.get('own_usage'), def_own_usage)
        sim_tariff_rate = safe_float(request.GET.get('tariff_rate'), def_tariff)
        sim_maint_val = safe_float(request.GET.get('maint_val'), def_maint)
        sim_tax_pct = safe_float(request.GET.get('tax_pct'), def_tax)

        sim_monthly_exported = max(0, sim_monthly_gen - sim_own_usage)
        sim_gross_monthly = sim_monthly_exported * sim_tariff_rate
        sim_maint_monthly = sim_maint_val
        sim_net_monthly = sim_gross_monthly - sim_maint_monthly
        
        sim_gross_yearly = sim_gross_monthly * 12
        sim_maint_yearly = sim_maint_monthly * 12
        sim_tax_yearly = sim_gross_yearly * (sim_tax_pct / 100.0)
        sim_net_yearly = sim_net_monthly * 12
        
        sim_projections = []
        cumulative = 0
        break_even_year = 0
        chart_cumulative_data = []
        chart_investment_data = []
        
        current_year = datetime.date.today().year
        monthly_cumulative = 0
        if sim_net_yearly > 0:
            import math
            min_projection_years = int(math.ceil(sim_project_cost / sim_net_yearly))
        else:
            min_projection_years = 1
            
        try:
            projection_years = int(request.GET.get('projection_years', 20))
        except ValueError:
            projection_years = 20
            
        projection_years = max(projection_years, min_projection_years)
        
        import time
        current_date = datetime.date.today()
        # Strictly align chart timeline with the table's calendar year (Jan 1st)
        chart_date = datetime.date(current_date.year, 1, 1)
        
        for i in range(1, projection_years + 1):
            actual_year = current_year + i - 1
            cumulative += sim_net_yearly
            sim_roi = (cumulative / sim_project_cost) * 100 if sim_project_cost > 0 else 0
            
            sim_recovered_pct = (cumulative / sim_project_cost) * 100 if sim_project_cost > 0 else 0
            sim_remaining_pct = max(0, 100 - sim_recovered_pct)
            
            is_break_even = False
            break_even_month_name = None
            if break_even_year == 0 and cumulative >= sim_project_cost and sim_net_yearly > 0:
                is_break_even = True
                break_even_year = i
            
            months_data = []
            m_recovered = (cumulative - sim_net_yearly) / sim_project_cost * 100 if sim_project_cost > 0 else 0
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            for m in month_names:
                monthly_cumulative += sim_net_monthly
                m_recovered += (sim_net_monthly / sim_project_cost) * 100 if sim_project_cost > 0 else 0
                
                if is_break_even and break_even_month_name is None and monthly_cumulative >= sim_project_cost:
                    break_even_month_name = m
                    
                timestamp_ms = int(time.mktime(chart_date.timetuple())) * 1000
                chart_cumulative_data.append([timestamp_ms, monthly_cumulative])
                chart_investment_data.append([timestamp_ms, sim_project_cost])
                
                # Advance chart_date by 1 month
                if chart_date.month == 12:
                    chart_date = datetime.date(chart_date.year + 1, 1, 1)
                else:
                    chart_date = datetime.date(chart_date.year, chart_date.month + 1, 1)
                    
                months_data.append({
                    'name': m,
                    'profit': sim_net_monthly,
                    'cumulative': monthly_cumulative,
                    'remaining_pct': max(0, 100 - m_recovered)
                })
                
            sim_projections.append({
                'year': i,
                'actual_year': actual_year,
                'profit': sim_net_yearly,
                'cumulative': cumulative,
                'roi': sim_roi,
                'remaining_pct': sim_remaining_pct,
                'is_break_even': is_break_even,
                'break_even_month': break_even_month_name,
                'months': months_data
            })

        if sim_net_yearly <= 0:
            sim_break_even_text = "Never (No Profit)"
        else:
            years = sim_project_cost / sim_net_yearly
            whole_years = int(years)
            months = int(round((years - whole_years) * 12))
            if months == 12:
                whole_years += 1
                months = 0
            sim_break_even_text = f"{whole_years} Years, {months} Months"

        sim_proj_net = sim_net_yearly * projection_years
        sim_proj_maint = sim_maint_yearly * projection_years
        sim_proj_tax = 0
        chart_donut_data = [sim_proj_net, sim_proj_maint, sim_proj_tax]

        # History Tracking
        is_simulation_update = 'project_cost' in request.GET
        is_view_only = request.GET.get('view_only') == '1'
        
        if is_simulation_update and not is_view_only:
            last_sim = SolarCalculation.objects.filter(user=request.user, sim_project_cost__isnull=False).order_by('-created_at').first()
            
            should_save = False
            if not last_sim:
                should_save = True
            else:
                try:
                    if float(last_sim.sim_project_cost) != float(sim_project_cost) or \
                       float(last_sim.sim_monthly_gen) != float(sim_monthly_gen) or \
                       float(last_sim.sim_tariff_rate) != float(sim_tariff_rate) or \
                       float(last_sim.sim_maint_val) != float(sim_maint_val) or \
                       float(last_sim.sim_tax_pct) != float(sim_tax_pct) or \
                       float(last_sim.sim_own_usage) != float(sim_own_usage):
                        should_save = True
                except (ValueError, TypeError):
                    should_save = True

            if should_save:
                try:
                    SolarCalculation.objects.create(
                    user=request.user,
                    monthly_bill=0,
                    investment=sim_project_cost,
                    annual_savings=sim_net_yearly,
                    three_year=sim_net_yearly * 3,
                    five_year=sim_net_yearly * 5,
                    ten_year=sim_net_yearly * 10,
                    fifteen_year=sim_net_yearly * 15,
                    twenty_year=sim_net_yearly * 20,
                    roi=max(-999.99, min(sim_roi, 999.99)),
                    break_even=break_even_year,
                    maintenance_cost=sim_maint_yearly,
                    carbon_saved=0,
                    trees_saved=0,
                    net_profit=sim_net_yearly,
                    future_value=0,
                    sim_project_cost=sim_project_cost,
                    sim_monthly_gen=sim_monthly_gen,
                    sim_own_usage=sim_own_usage,
                    sim_tariff_rate=max(-999.99, min(sim_tariff_rate, 999.99)),
                    sim_maint_val=sim_maint_val,
                    sim_tax_pct=max(-999.99, min(sim_tax_pct, 999.99)),
                    sim_net_yearly=sim_net_yearly
                )
                except Exception as e:
                    print(f"Error saving calculation: {e}")

        # Fetch History for Table
        simulation_history = SolarCalculation.objects.filter(user=request.user, sim_project_cost__isnull=False).order_by('-created_at')[:5]

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
            'latest_maintenance_val': latest_maintenance_val,
            'latest_tax_pct': latest_tax_pct,
            'notifications': client.notifications.order_by('-date')[:5] if client else [],
            
            # Simulator Context
            'sim_project_cost': sim_project_cost,
            'sim_monthly_gen': sim_monthly_gen,
            'sim_own_usage': sim_own_usage,
            'sim_tariff_rate': sim_tariff_rate,
            'sim_maint_val': sim_maint_val,
            'sim_tax_pct': sim_tax_pct,
            
            'sim_monthly_exported': sim_monthly_exported,
            'sim_gross_monthly': sim_gross_monthly,
            'sim_maint_monthly': sim_maint_monthly,
            'sim_net_monthly': sim_net_yearly / 12,
            'sim_net_yearly': sim_net_yearly,
            'sim_break_even_text': sim_break_even_text,
            'sim_projections': sim_projections,
            'simulation_history': simulation_history,
            'projection_years': projection_years,
            'min_projection_years': min_projection_years,
            
            'chart_cumulative_data': json.dumps(chart_cumulative_data),
            'chart_investment_data': json.dumps(chart_investment_data),
            'chart_donut_data': json.dumps(chart_donut_data),
        })
        


    return render(request, 'solar/dashboard.html', context)

@login_required(login_url='login')
def dashboard_charts_api_view(request):
    try:
        client = request.user.client_profile
        plants = client.plants.all()
        client_inv = sum(p.client_investment for p in plants)
        company_inv = sum(p.company_investment for p in plants)
        
        # Get last 6 months labels and data
        today = datetime.date.today()
        month_labels = []
        gen_data = []
        rev_data = []
        carbon_data = []
        
        cumulative_carbon = 0
        
        for i in range(5, -1, -1):
            target_month = today.month - i
            target_year = today.year
            if target_month <= 0:
                target_month += 12
                target_year -= 1
                
            month_abbr = datetime.date(target_year, target_month, 1).strftime('%b %Y')
            month_labels.append(month_abbr)
            
            # Daily readings summed for the month
            readings = MeterReading.objects.filter(
                plant__in=plants, 
                reading_date__year=target_year, 
                reading_date__month=target_month
            )
            d_gen = sum(r.daily_generation for r in readings)
            gen_data.append(float(d_gen))
            
            # Payments for the month
            payments = Payment.objects.filter(
                plant__in=plants,
                month__year=target_year,
                month__month=target_month
            )
            m_rev = sum(p.net_earnings for p in payments)
            rev_data.append(float(m_rev))
            
            # Carbon offset: approx 0.85 kg CO2 per kWh
            cumulative_carbon += float(d_gen) * 0.85
            carbon_data.append(round(cumulative_carbon, 2))

        # Overall revenue distribution
        gross = 0
        maint = 0
        tax = 0
        net = 0
        for plant in plants:
            for p in plant.payments.all():
                gross += float(p.gross_revenue)
                maint += float(p.maintenance_charge)
                tax += float(p.tax_amount)
                net += float(p.net_earnings)

        data = {
            'performance': {
                'labels': month_labels,
                'generation': gen_data,
                'revenue': rev_data
            },
            'environmental': {
                'labels': month_labels,
                'carbon_offset': carbon_data
            },
            'investment_dist': {
                'labels': ['Client Investment', 'Company Investment'],
                'data': [float(client_inv), float(company_inv)]
            },
            'revenue_dist': {
                'labels': ['Net Earnings', 'Maintenance', 'Tax'],
                'data': [net, maint, tax]
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
    calculations = SolarCalculation.objects.filter(user=request.user, sim_project_cost__isnull=False).order_by('-created_at')
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
