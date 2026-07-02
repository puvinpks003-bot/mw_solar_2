import re

with open('templates/solar/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_grid = """    <!-- 14 KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        
        <div class="glass-card rounded-xl p-5 border-l-4 border-blue-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Project Cost</p>
            <h3 class="text-2xl font-bold text-white">₹{{ project_cost|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-blue-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Client Investment</p>
            <h3 class="text-2xl font-bold text-white">₹{{ client_investment|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-purple-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Company Investment</p>
            <h3 class="text-2xl font-bold text-white">₹{{ company_investment|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-green-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Current Value</p>
            <h3 class="text-2xl font-bold text-white">₹{{ current_project_value|floatformat:0 }}</h3>
        </div>

        <div class="glass-card rounded-xl p-5 border-l-4 border-yellow-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Today's Gen</p>
            <h3 class="text-2xl font-bold text-white">{{ todays_generation|floatformat:1 }} kWh</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-yellow-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Monthly Gen</p>
            <h3 class="text-2xl font-bold text-white">{{ monthly_generation|floatformat:1 }} kWh</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-yellow-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Lifetime Gen</p>
            <h3 class="text-2xl font-bold text-white">{{ lifetime_generation|floatformat:1 }} kWh</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-yellow-400">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Exported Units</p>
            <h3 class="text-2xl font-bold text-white">{{ electricity_exported|floatformat:1 }} kWh</h3>
        </div>

        <div class="glass-card rounded-xl p-5 border-l-4 border-emerald-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Gross Revenue</p>
            <h3 class="text-2xl font-bold text-white">₹{{ gross_revenue|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-red-500">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Maintenance</p>
            <h3 class="text-2xl font-bold text-white">₹{{ maintenance_charges|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-emerald-400">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Net Earnings</p>
            <h3 class="text-2xl font-bold text-white">₹{{ net_earnings|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-blue-400">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Actual ROI</p>
            <h3 class="text-2xl font-bold text-white">{{ roi|floatformat:1 }}%</h3>
        </div>

        <div class="glass-card rounded-xl p-5 border-l-4 border-gray-400 col-span-1 sm:col-span-2">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Latest Payment Status</p>
            <h3 class="text-2xl font-bold text-white">{{ payment_status }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-l-4 border-orange-500 col-span-1 sm:col-span-2 overflow-y-auto max-h-24">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Recent Notifications</p>
            <ul class="text-sm text-gray-300">
                {% for note in notifications %}
                    <li class="mb-1"><i class="fa-solid fa-bell text-orange-400 mr-2 text-xs"></i>{{ note.title }} - {{ note.date|date:"M d" }}</li>
                {% empty %}
                    <li>No recent notifications.</li>
                {% endfor %}
            </ul>
        </div>

    </div>"""

new_grid = """    <!-- 14 KPI Cards (Rearranged into sections) -->
    
    <!-- Section: Investment & Value -->
    <h3 class="text-lg font-medium text-gray-300 mb-3 border-b border-gray-800 pb-2"><i class="fa-solid fa-sack-dollar text-blue-500 mr-2"></i>Investment Summary</h3>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="glass-card rounded-xl p-5 border-t-4 border-blue-500 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Project Cost</p>
            <h3 class="text-2xl font-bold text-white">₹{{ project_cost|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-blue-400 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Client Investment</p>
            <h3 class="text-2xl font-bold text-white">₹{{ client_investment|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-purple-500 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Company Investment</p>
            <h3 class="text-2xl font-bold text-white">₹{{ company_investment|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-green-500 hover:bg-gray-800/50 transition-colors relative overflow-hidden">
            <div class="absolute -right-4 -bottom-4 opacity-10"><i class="fa-solid fa-chart-line text-6xl"></i></div>
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Current Value</p>
            <h3 class="text-2xl font-bold text-emerald-400">₹{{ current_project_value|floatformat:0 }}</h3>
        </div>
    </div>

    <!-- Section: Generation & Operations -->
    <h3 class="text-lg font-medium text-gray-300 mb-3 border-b border-gray-800 pb-2"><i class="fa-solid fa-solar-panel text-yellow-500 mr-2"></i>Generation & Export</h3>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="glass-card rounded-xl p-5 border-t-4 border-yellow-500 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Today's Gen</p>
            <h3 class="text-2xl font-bold text-white">{{ todays_generation|floatformat:1 }} <span class="text-sm font-normal text-gray-500">kWh</span></h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-yellow-400 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Monthly Gen</p>
            <h3 class="text-2xl font-bold text-white">{{ monthly_generation|floatformat:1 }} <span class="text-sm font-normal text-gray-500">kWh</span></h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-orange-500 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Lifetime Gen</p>
            <h3 class="text-2xl font-bold text-white">{{ lifetime_generation|floatformat:1 }} <span class="text-sm font-normal text-gray-500">kWh</span></h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-cyan-400 hover:bg-gray-800/50 transition-colors relative overflow-hidden">
            <div class="absolute -right-2 -bottom-2 opacity-10"><i class="fa-solid fa-plug-circle-bolt text-5xl"></i></div>
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Exported Units</p>
            <h3 class="text-2xl font-bold text-cyan-400">{{ electricity_exported|floatformat:1 }} <span class="text-sm font-normal text-gray-500">kWh</span></h3>
        </div>
    </div>

    <!-- Section: Financial Returns -->
    <h3 class="text-lg font-medium text-gray-300 mb-3 border-b border-gray-800 pb-2"><i class="fa-solid fa-money-bill-trend-up text-emerald-500 mr-2"></i>Financial Returns</h3>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="glass-card rounded-xl p-5 border-t-4 border-emerald-500 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Gross Revenue</p>
            <h3 class="text-2xl font-bold text-white">₹{{ gross_revenue|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-red-500 hover:bg-gray-800/50 transition-colors">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Maintenance</p>
            <h3 class="text-2xl font-bold text-white">₹{{ maintenance_charges|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-emerald-400 hover:bg-gray-800/50 transition-colors relative overflow-hidden">
            <div class="absolute -right-2 -bottom-2 opacity-10"><i class="fa-solid fa-wallet text-5xl"></i></div>
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Net Earnings</p>
            <h3 class="text-2xl font-bold text-emerald-400">₹{{ net_earnings|floatformat:0 }}</h3>
        </div>
        <div class="glass-card rounded-xl p-5 border-t-4 border-indigo-500 hover:bg-gray-800/50 transition-colors bg-gradient-to-br from-gray-900 to-indigo-900/20">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Actual ROI</p>
            <h3 class="text-2xl font-bold text-white">{{ roi|floatformat:2 }}%</h3>
        </div>
    </div>

    <!-- Section: Account & Alerts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-10">
        <div class="glass-card rounded-xl p-6 border-l-4 border-gray-400 flex items-center justify-between">
            <div>
                <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-1">Latest Payment Status</p>
                <h3 class="text-xl font-bold {% if payment_status == 'COMPLETED' %}text-emerald-400{% else %}text-white{% endif %}">{{ payment_status }}</h3>
            </div>
            <i class="fa-solid fa-file-invoice-dollar text-4xl text-gray-600"></i>
        </div>
        <div class="glass-card rounded-xl p-6 border-l-4 border-orange-500 flex flex-col justify-center">
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Recent Notifications</p>
            <ul class="text-sm text-gray-300 space-y-2 overflow-y-auto max-h-24">
                {% for note in notifications %}
                    <li class="flex items-start"><i class="fa-solid fa-bell text-orange-400 mt-1 mr-2 text-xs"></i><span><strong class="text-white">{{ note.title }}</strong><br/><span class="text-xs text-gray-500">{{ note.date|date:"M d, Y" }}</span></span></li>
                {% empty %}
                    <li class="text-gray-500 italic">No recent notifications.</li>
                {% endfor %}
            </ul>
        </div>
    </div>"""

if old_grid in content:
    content = content.replace(old_grid, new_grid)
    with open('templates/solar/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced successfully!")
else:
    print("Could not find the exact old_grid string to replace.")
