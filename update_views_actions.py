import re

with open('solar/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update dashboard_view to accept calc_id
old_dashboard_view = """def dashboard_view(request):
    context = {}
    latest_calc = SolarCalculation.objects.filter(user=request.user).first()
    context['latest_calc'] = latest_calc"""

new_dashboard_view = """from django.shortcuts import get_object_or_404

@login_required(login_url='login')
def dashboard_view(request):
    context = {}
    calc_id = request.GET.get('calc_id')
    
    if calc_id:
        latest_calc = get_object_or_404(SolarCalculation, id=calc_id, user=request.user)
        context['force_show_calc'] = True
    else:
        latest_calc = SolarCalculation.objects.filter(user=request.user).order_by('-created_at').first()
        
    context['latest_calc'] = latest_calc"""

content = content.replace("@login_required(login_url='login')\ndef dashboard_view(request):\n    context = {}\n    latest_calc = SolarCalculation.objects.filter(user=request.user).first()\n    context['latest_calc'] = latest_calc", new_dashboard_view)

# Add delete_calculation_view at the end
delete_view = """
@login_required(login_url='login')
def delete_calculation_view(request, calc_id):
    if request.method == 'POST':
        calc = get_object_or_404(SolarCalculation, id=calc_id, user=request.user)
        calc.delete()
        messages.success(request, "Calculation deleted successfully.")
    return redirect('history')
"""
content += delete_view

with open('solar/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated views.py")
