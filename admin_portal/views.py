from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from solar.models import CustomUser, SolarCalculation
from solar.forms import LoginForm, SignupForm
from solar.views import get_dashboard_context
from django.urls import reverse

def admin_auth_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_portal:admin_dashboard')
        else:
            messages.info(request, "You are logged in as a standard user. Redirecting to your dashboard.")
            return redirect('dashboard')
    
    login_form = LoginForm()
    signup_form = SignupForm()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                mobile_number = login_form.cleaned_data.get('mobile_number')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, mobile_number=mobile_number, password=password)
                if user is not None:
                    if user.is_staff:
                        login(request, user)
                        return redirect('admin_portal:admin_dashboard')
                    else:
                        messages.error(request, "This account does not have admin privileges.")
                else:
                    messages.error(request, "Invalid mobile number or password.")
                    
        elif action == 'signup':
            signup_form = SignupForm(request.POST)
            passphrase = request.POST.get('passphrase')
            
            if passphrase != 'MWSOLAR2026':  # Hardcoded secret passphrase
                messages.error(request, "Invalid admin passphrase.")
            elif signup_form.is_valid():
                user = signup_form.save(commit=False)
                user.set_password(signup_form.cleaned_data['password'])
                user.is_staff = True
                user.is_superuser = True
                user.save()
                login(request, user, backend='solar.authentication.MobileNumberBackend')
                messages.success(request, "Admin account created successfully!")
                return redirect('admin_portal:admin_dashboard')
                
    return render(request, 'admin_portal/admin_auth.html', {
        'login_form': login_form,
        'signup_form': signup_form
    })

def admin_logout_view(request):
    logout(request)
    return redirect('admin_portal:admin_auth')

@login_required(login_url='admin_portal:admin_auth')
def admin_dashboard_view(request):
    if not request.user.is_staff:
        return redirect('admin_portal:admin_auth')
        
    all_users = CustomUser.objects.filter(is_staff=False).order_by('-date_joined')
    all_calculations = SolarCalculation.objects.all().order_by('-created_at')
    
    # KPI Calculations
    total_users = all_users.count()
    total_simulations = all_calculations.count()
    
    # Calculate average project cost (ignoring null or 0)
    valid_costs = [c.sim_project_cost for c in all_calculations if c.sim_project_cost and float(c.sim_project_cost) > 0]
    average_cost = sum(valid_costs) / len(valid_costs) if valid_costs else 0
    
    return render(request, 'admin_portal/admin_dashboard.html', {
        'all_users': all_users,
        'all_calculations': all_calculations,
        'total_users': total_users,
        'total_simulations': total_simulations,
        'average_cost': average_cost,
    })

@login_required(login_url='admin_portal:admin_auth')
def admin_delete_user_view(request, user_id):
    if not request.user.is_staff:
        return redirect('admin_portal:admin_auth')
        
    if request.method == 'POST':
        user_to_delete = get_object_or_404(CustomUser, id=user_id)
        if not user_to_delete.is_superuser:  # Prevent deleting other superusers
            user_to_delete.delete()
            messages.success(request, f"User {user_to_delete.full_name} has been deleted.")
        else:
            messages.error(request, "Cannot delete another administrator.")
            
    return redirect('admin_portal:admin_dashboard')

@login_required(login_url='admin_portal:admin_auth')
def admin_user_dashboard_view(request, user_id):
    if not request.user.is_staff:
        return redirect('admin_portal:admin_auth')
        
    target_user = get_object_or_404(CustomUser, id=user_id, is_staff=False)
    
    # We pass view_only=True so the admin cannot accidentally save new calculations for the user
    context = get_dashboard_context(request, target_user, view_only=True)
    
    # Override dashboard url so the HTMX forms and buttons hit this view instead of the standard dashboard
    context['dashboard_url'] = reverse('admin_portal:admin_user_dashboard', args=[target_user.id])
    context['target_user'] = target_user
    
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'admin_portal/admin_user_dashboard.html', context)
        
    return render(request, 'admin_portal/admin_user_dashboard.html', context)
