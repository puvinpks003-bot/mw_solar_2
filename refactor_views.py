import os

source_file = 'solar/views.py'
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

dashboard_start = -1
dashboard_end = -1
for i, line in enumerate(lines):
    if line.startswith('@login_required(login_url=\'login\')') and 'def dashboard_view(request):' in lines[i+1]:
        dashboard_start = i
    if dashboard_start != -1 and line.startswith('def dashboard_charts_api_view'):
        dashboard_end = i - 2
        break

# Extracted lines (body of dashboard_view)
dashboard_lines = lines[dashboard_start:dashboard_end]

# Let's write the new functions manually.
# dashboard_lines contains:
# @login_required(...)
# def dashboard_view(request):
#     if request.user.is_staff: ...

# We will define get_dashboard_context
new_func_def = """
from django.urls import reverse

def get_dashboard_context(request, target_user, view_only=False):
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
    
    # 1. Gather Inputs (from GET or DB defaults)
    sim_project_cost = float(request.GET.get('project_cost', context['project_cost']))
    sim_monthly_gen = float(request.GET.get('monthly_gen', monthly_gen))
    sim_own_usage = float(request.GET.get('own_usage', own_usage))
    sim_tariff_rate = float(request.GET.get('tariff_rate', latest_tariff_rate))
    sim_maint_val = float(request.GET.get('maint_val', latest_maintenance_val))
    sim_tax_pct = float(request.GET.get('tax_pct', latest_tax_pct))
    
    projection_years = int(request.GET.get('projection_years', 20))
    min_projection_years = 20

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
    chart_donut_data = [
        float(sim_net_yearly),
        float(sim_maint_val * 12),
        float(sim_gross_monthly * 12 * (sim_tax_pct / 100))
    ]

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
        
        # Only add to template projections if it's within the requested projection_years OR it's the break-even year
        if year <= projection_years or year_is_break_even:
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

    # 3. Handle Saving the Simulation via GET if values changed
    # Only save if we are actively updating parameters (GET has project_cost)
    is_simulation_update = 'project_cost' in request.GET
    
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
                sim_tax_pct=sim_tax_pct
            )
            context['force_redirect'] = True
            context['new_calc_id'] = new_calc.id

    # Add all calculated variables to context
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
        'sim_projections': sim_projections,
        'sim_break_even_text': sim_break_even_text,
        
        # Pass JSON data for JS Charts
        'chart_cumulative_data': json.dumps(chart_cumulative_data),
        'chart_investment_data': json.dumps(chart_investment_data),
        'chart_donut_data': json.dumps(chart_donut_data),
        
        # History
        'simulation_history': SolarCalculation.objects.filter(user=target_user, sim_project_cost__isnull=False).order_by('-created_at')[:5]
    })
    
    return context

@login_required(login_url='login')
def dashboard_view(request):
    if request.user.is_staff:
        return redirect('admin_portal:admin_dashboard')
        
    context = get_dashboard_context(request, request.user, view_only=False)
    
    if context.get('force_redirect'):
        if request.headers.get('HX-Request') == 'true':
            context['dashboard_url'] = reverse('dashboard')
            return render(request, 'solar/dashboard.html', context)
        url = f"{reverse('dashboard')}?calc_id={context['new_calc_id']}"
        return redirect(url)
        
    # We must also ensure view_only from GET is respected (if user clicks a history link)
    is_view_only = request.GET.get('view_only') == '1'
    if is_view_only:
        context = get_dashboard_context(request, request.user, view_only=True)
        
    context['dashboard_url'] = reverse('dashboard')
    
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'solar/dashboard.html', context)

    return render(request, 'solar/dashboard.html', context)
"""

new_content = ''.join(lines[:dashboard_start]) + new_func_def + '\n' + ''.join(lines[dashboard_end+1:])

with open(source_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Successfully refactored views.py')
