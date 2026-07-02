import re

with open('templates/solar/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_ui_block = """
    {% if has_client %}
    <div class="mt-8 mb-4">
        <h2 class="text-2xl font-bold text-white tracking-tight">Live Plant Data</h2>
        <p class="text-gray-400 mt-1">Real-time metrics from your connected solar plants.</p>
    </div>
    
    <!-- 14 KPI Cards -->
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

    </div>

    <!-- 6 New Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- 1. Monthly Solar Gen (Line) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Monthly Solar Generation</h3>
            <canvas id="chartMonthlyGen" class="w-full h-64"></canvas>
        </div>
        <!-- 2. Monthly Revenue (Bar) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Monthly Revenue</h3>
            <canvas id="chartMonthlyRev" class="w-full h-64"></canvas>
        </div>
        <!-- 3. Investment Dist (Pie) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Investment Distribution</h3>
            <div id="chartInvestmentDist" class="w-full h-64 flex justify-center items-center"></div>
        </div>
        <!-- 4. Revenue Dist (Pie) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Revenue Distribution</h3>
            <div id="chartRevenueDist" class="w-full h-64 flex justify-center items-center"></div>
        </div>
        <!-- 5. Export Trend (Line) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Electricity Export Trend</h3>
            <canvas id="chartExportTrend" class="w-full h-64"></canvas>
        </div>
        <!-- 6. Lifetime Prod (Area) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Lifetime Production</h3>
            <div id="chartLifetimeProd" class="w-full h-64 flex justify-center items-center"></div>
        </div>
    </div>
    {% endif %}
"""

js_block = """
{% if has_client %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        fetch('/api/charts/')
            .then(response => response.json())
            .then(data => {
                // 1. Monthly Gen (Line - Chart.js)
                new Chart(document.getElementById('chartMonthlyGen').getContext('2d'), {
                    type: 'line',
                    data: { labels: data.monthly_gen.labels, datasets: [{ label: 'Generation (kWh)', data: data.monthly_gen.data, borderColor: '#f59e0b', tension: 0.4, fill: true, backgroundColor: 'rgba(245, 158, 11, 0.1)' }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
                });

                // 2. Monthly Rev (Bar - Chart.js)
                new Chart(document.getElementById('chartMonthlyRev').getContext('2d'), {
                    type: 'bar',
                    data: { labels: data.monthly_revenue.labels, datasets: [{ label: 'Revenue (₹)', data: data.monthly_revenue.data, backgroundColor: '#10b981', borderRadius: 4 }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
                });

                // 3. Investment Dist (Pie - ApexCharts)
                new ApexCharts(document.querySelector("#chartInvestmentDist"), {
                    series: data.investment_dist.data, labels: data.investment_dist.labels,
                    chart: { type: 'pie', height: '100%', foreColor: '#9ca3af' }, colors: ['#3b82f6', '#8b5cf6'], stroke: { show: false }, legend: { position: 'bottom' }, tooltip: { theme: 'dark' }
                }).render();

                // 4. Revenue Dist (Pie - ApexCharts)
                new ApexCharts(document.querySelector("#chartRevenueDist"), {
                    series: data.revenue_dist.data, labels: data.revenue_dist.labels,
                    chart: { type: 'pie', height: '100%', foreColor: '#9ca3af' }, colors: ['#10b981', '#ef4444', '#f59e0b'], stroke: { show: false }, legend: { position: 'bottom' }, tooltip: { theme: 'dark' }
                }).render();

                // 5. Export Trend (Line - Chart.js)
                new Chart(document.getElementById('chartExportTrend').getContext('2d'), {
                    type: 'line',
                    data: { labels: data.export_trend.labels, datasets: [{ label: 'Exported (kWh)', data: data.export_trend.data, borderColor: '#3b82f6', tension: 0.1 }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
                });

                // 6. Lifetime Prod (Area - ApexCharts)
                new ApexCharts(document.querySelector("#chartLifetimeProd"), {
                    series: [{ name: 'Cumulative Prod (kWh)', data: data.lifetime_prod.data }],
                    chart: { type: 'area', height: '100%', foreColor: '#9ca3af', toolbar: { show: false } },
                    xaxis: { categories: data.lifetime_prod.labels },
                    colors: ['#06b6d4'], fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.5, opacityTo: 0.1 } },
                    stroke: { curve: 'smooth', width: 2 }, dataLabels: { enabled: false }, grid: { borderColor: 'rgba(255,255,255,0.05)' }, tooltip: { theme: 'dark' }
                }).render();
            });
    });
</script>
{% endif %}
"""

# Replace {% if latest_calc %} with {% if has_client or latest_calc %}
content = content.replace('{% if latest_calc %}', '{% if has_client or latest_calc %}')

# Inject new_ui_block before <!-- Top Stats Cards --> (which is inside the {% if %})
content = content.replace('<!-- Top Stats Cards -->', new_ui_block + '\n    <!-- Top Stats Cards -->')

# Inject js_block at the end of extra_scripts
content = content.replace('{% endblock %}', js_block + '\n{% endblock %}')

with open('templates/solar/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
