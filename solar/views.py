from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
import datetime
import json
from django.http import JsonResponse
from django.contrib.auth import logout

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
        if request.user.is_staff:
            return redirect('admin_portal:admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            mobile_number = form.cleaned_data.get('mobile_number')
            password = form.cleaned_data.get('password')
            user = authenticate(request, mobile_number=mobile_number, password=password)
            if user is not None:
                if user.is_staff:
                    messages.error(request, "Administrators must log in through the Admin Portal.")
                    return redirect('login')
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



from django.urls import reverse

def get_dashboard_context(request, target_user, view_only=False):
    context = {}
    context['view_only'] = view_only
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
        latest_calc = get_object_or_404(SolarCalculation, id=calc_id, user=target_user)
        context['force_show_calc'] = True
    else:
        latest_calc = SolarCalculation.objects.filter(user=target_user).order_by('-created_at').first()
        
    context['latest_calc'] = latest_calc
    
    try:
        client = target_user.client_profile
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
        
        # Optimize DB Calls using Aggregation
        readings = MeterReading.objects.filter(plant__in=plants)
        payments = Payment.objects.filter(plant__in=plants)

        # Monthly Stats
        m_agg = readings.filter(
            reading_date__month=today.month,
            reading_date__year=today.year
        ).aggregate(
            m_gen=Sum('monthly_generation'),
            m_own=Sum('self_consumption'),
            m_exp=Sum('electricity_exported')
        )
        monthly_gen = m_agg['m_gen'] or 0
        own_usage = m_agg['m_own'] or 0
        monthly_exported_units = m_agg['m_exp'] or 0

        # Total Stats
        tot_agg = readings.aggregate(
            t_gen=Sum('lifetime_generation'),
            e_exp=Sum('electricity_exported')
        )
        lifetime_gen = tot_agg['t_gen'] or 0
        exported_units = tot_agg['e_exp'] or 0

        # Payments Stats
        pay_agg = payments.aggregate(
            g_rev=Sum('gross_revenue'),
            m_chg=Sum('maintenance_charge'),
            n_ear=Sum('net_earnings')
        )
        gross_revenue = pay_agg['g_rev'] or 0
        maintenance = pay_agg['m_chg'] or 0
        net_earnings = pay_agg['n_ear'] or 0
        yearly_data_dict = {}
        for plant in plants:
            plant_payments = plant.payments.all()
            for p in plant_payments:
                year = p.month.year
                if year not in yearly_data_dict:
                    yearly_data_dict[year] = {
                        'year': year,
                        'profit': 0,
                        'investment': float(plant.total_investment),
                    }
                yearly_data_dict[year]['profit'] += float(p.net_earnings)
                
            latest_payment = plant_payments.order_by('-payment_date').first()
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
                latest_tax_pct = float(latest_payment.tax_amount / latest_payment.gross_revenue * 100) if latest_payment.gross_revenue else 0
                
    except Exception as e:
        # User is not a client
        print("Error fetching client profile:", e)
        pass

    # ==========================================
    # Interactive Simulator Logic
    # ==========================================
    
    # Base defaults
    def_project_cost = context['project_cost']
    def_monthly_gen = monthly_gen
    def_own_usage = own_usage
    def_tariff_rate = latest_tariff_rate
    def_maint_val = latest_maintenance_val
    def_tax_pct = latest_tax_pct
    
    # If user doesn't have a client profile, default to their latest simulation history
    if not client:
        latest_sim = SolarCalculation.objects.filter(user=target_user, sim_project_cost__isnull=False).order_by('-created_at').first()
        if latest_sim:
            def_project_cost = latest_sim.sim_project_cost or 0
            def_monthly_gen = latest_sim.sim_monthly_gen or 0
            def_own_usage = latest_sim.sim_own_usage or 0
            def_tariff_rate = latest_sim.sim_tariff_rate or 0
            def_maint_val = latest_sim.sim_maint_val or 0
            def_tax_pct = latest_sim.sim_tax_pct or 0

    # 1. Gather Inputs (from GET or DB defaults)
    sim_project_cost = float(request.GET.get('project_cost', def_project_cost))
    sim_monthly_gen = float(request.GET.get('monthly_gen', def_monthly_gen))
    sim_own_usage = float(request.GET.get('own_usage', def_own_usage))
    sim_tariff_rate = float(request.GET.get('tariff_rate', def_tariff_rate))
    sim_maint_val = float(request.GET.get('maint_val', def_maint_val))
    sim_tax_pct = float(request.GET.get('tax_pct', def_tax_pct))
    
    projection_years = int(request.GET.get('projection_years', 20))
    min_projection_years = 1

    # 2. Run Python Calculations
    sim_monthly_exported = max(0, sim_monthly_gen - sim_own_usage)
    sim_gross_monthly = sim_monthly_exported * sim_tariff_rate
    sim_net_monthly = sim_gross_monthly - sim_maint_val
    sim_net_yearly = sim_net_monthly * 12
    
    # Generate Multi-Year Projections & Break-even logic
    sim_projections = []
    cumulative = 0
    is_break_even_found = False
    sim_break_even_text = "Not Reached"
    
    start_year = datetime.date.today().year
    
    # Always calculate up to at least 20 years or break-even, whichever is longer
    calc_years = max(projection_years, 20)
    
    chart_cumulative_data = []
    chart_investment_data = []

    for year in range(1, calc_years + 1):
        actual_year = start_year + year - 1
        
        # Monthly breakdown for the year
        months_data = []
        year_break_even_month = None
        year_is_break_even = False
        
        for m in range(1, 13):
            cumulative += sim_net_monthly
            
            # Record data for charts (approximate time for simplicity)
            chart_ts = int(datetime.datetime(actual_year, m, 1).timestamp() * 1000)
            chart_cumulative_data.append([chart_ts, float(cumulative)])
            chart_investment_data.append([chart_ts, float(sim_project_cost)])
            
            month_remaining_pct = max(0, ((sim_project_cost - cumulative) / sim_project_cost) * 100) if sim_project_cost > 0 else 0
            
            is_month_break_even = False
            if cumulative >= sim_project_cost and not is_break_even_found and sim_project_cost > 0:
                is_break_even_found = True
                year_is_break_even = True
                is_month_break_even = True
                year_break_even_month = datetime.date(2000, m, 1).strftime('%b')
                sim_break_even_text = f"Year {year}, {year_break_even_month}"
                min_projection_years = year
            
            months_data.append({
                'name': datetime.date(2000, m, 1).strftime('%b'),
                'profit': round(sim_net_monthly, 2),
                'cumulative': round(cumulative, 2),
                'remaining_pct': round(month_remaining_pct, 2),
                'is_break_even': is_month_break_even
            })
            
        remaining_pct = max(0, ((sim_project_cost - cumulative) / sim_project_cost) * 100) if sim_project_cost > 0 else 0
        roi_pct = (sim_net_yearly / sim_project_cost * 100) if sim_project_cost > 0 else 0
        
        # Add to template projections unconditionally; we will slice it later
        sim_projections.append({
            'year': year,
            'actual_year': actual_year,
            'profit': round(sim_net_yearly, 2),
            'cumulative': round(cumulative, 2),
            'roi': round(roi_pct, 2),
            'remaining_pct': round(remaining_pct, 2),
            'months': months_data,
            'is_break_even': year_is_break_even,
            'break_even_month': year_break_even_month
        })

    # Enforce minimum projection years if break-even is found
    if is_break_even_found and projection_years < min_projection_years:
        projection_years = min_projection_years
        
    # Truncate chart data to match the display years
    display_years = projection_years
    
    # Slice the projections list to only show up to display_years
    sim_projections = sim_projections[:display_years]
    months_to_display = display_years * 12
    chart_cumulative_data = chart_cumulative_data[:months_to_display]
    chart_investment_data = chart_investment_data[:months_to_display]
    
    chart_donut_data = [
        float(sim_net_yearly * display_years),
        float(sim_maint_val * 12 * display_years),
        float(sim_gross_monthly * 12 * (sim_tax_pct / 100) * display_years)
    ]

    # 3. Handle Saving the Simulation via GET if values changed
    # Only save if we are actively updating parameters (GET has project_cost) and not just loading from history
    is_simulation_update = 'project_cost' in request.GET and request.GET.get('load_history') != '1'
    
    if is_simulation_update and not view_only:
        # Check if latest calc has same params
        last_sim = SolarCalculation.objects.filter(user=target_user, sim_project_cost__isnull=False).order_by('-created_at').first()
        
        changed = True
        if last_sim:
            changed = (
                float(last_sim.sim_project_cost or 0) != sim_project_cost or
                float(last_sim.sim_monthly_gen or 0) != sim_monthly_gen or
                float(last_sim.sim_own_usage or 0) != sim_own_usage or
                float(last_sim.sim_tariff_rate or 0) != sim_tariff_rate or
                float(last_sim.sim_maint_val or 0) != sim_maint_val
            )
            
        if changed:
            # Create a new history record
            new_calc = SolarCalculation.objects.create(
                user=target_user,
                monthly_bill=0, investment=0, annual_savings=0, three_year=0, five_year=0,
                ten_year=0, fifteen_year=0, twenty_year=0, roi=0, break_even=0,
                maintenance_cost=0, carbon_saved=0, trees_saved=0, net_profit=0, future_value=0,
                # New fields
                sim_project_cost=sim_project_cost,
                sim_monthly_gen=sim_monthly_gen,
                sim_own_usage=sim_own_usage,
                sim_tariff_rate=sim_tariff_rate,
                sim_maint_val=sim_maint_val,
                sim_tax_pct=sim_tax_pct,
                sim_net_yearly=sim_net_yearly
            )
            context['force_redirect'] = True
            context['new_calc_id'] = new_calc.id

    # Add all calculated variables to context
    history_qs = SolarCalculation.objects.filter(user=target_user, sim_project_cost__isnull=False).order_by('-created_at')
    
    context.update({
        'sim_project_cost': sim_project_cost,
        'sim_monthly_gen': sim_monthly_gen,
        'sim_own_usage': sim_own_usage,
        'sim_monthly_exported': sim_monthly_exported,
        'sim_tariff_rate': sim_tariff_rate,
        'sim_maint_val': sim_maint_val,
        'sim_tax_pct': sim_tax_pct,
        'sim_gross_monthly': sim_gross_monthly,
        'sim_maint_monthly': sim_maint_val,
        'sim_net_monthly': sim_net_monthly,
        'sim_net_yearly': sim_net_yearly,
        
        'projection_years': projection_years,
        'min_projection_years': min_projection_years,
        'display_years': display_years,
        'sim_projections': sim_projections,
        'sim_break_even_text': sim_break_even_text,
        
        # Pass JSON data for JS Charts
        'chart_cumulative_data': json.dumps(chart_cumulative_data),
        'chart_investment_data': json.dumps(chart_investment_data),
        'chart_donut_data': json.dumps(chart_donut_data),
        
        # History
        'simulation_history': history_qs if getattr(request.user, 'is_staff', False) else history_qs[:5]
    })
    
    return context

@login_required(login_url='login')
def dashboard_view(request):
    if request.user.is_staff:
        return redirect('admin_portal:admin_dashboard')
        
    is_view_only = request.GET.get('view_only') == '1'
    context = get_dashboard_context(request, request.user, view_only=is_view_only)
    
    if context.get('force_redirect'):
        if request.headers.get('HX-Request') == 'true':
            context['dashboard_url'] = reverse('dashboard')
            return render(request, 'solar/dashboard.html', context)
        url = f"{reverse('dashboard')}?calc_id={context['new_calc_id']}"
        return redirect(url)
        
    context['dashboard_url'] = reverse('dashboard')
    
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'solar/dashboard.html', context)

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
    if request.method == 'POST':
        user = request.user
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        profile_photo = request.FILES.get('profile_photo')
        
        if email and email != user.email:
            if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "This email address is already in use.")
                return render(request, 'solar/profile.html')
            user.email = email
            
        if full_name:
            user.full_name = full_name
            
        if profile_photo:
            user.profile_photo = profile_photo
            
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
        
    return render(request, 'solar/profile.html')

@login_required(login_url='login')
def delete_calculation_view(request, calc_id):
    if request.method == 'POST':
        calc = get_object_or_404(SolarCalculation, id=calc_id, user=request.user)
        calc.delete()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or request.accepts('application/json')
        if is_ajax:
            return JsonResponse({'status': 'success'})
        messages.success(request, "Calculation deleted successfully.")
    return redirect('history')

@login_required(login_url='login')
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, "Your account has been permanently deleted. We're sorry to see you go!")
        return redirect('landing')
    return redirect('profile')
