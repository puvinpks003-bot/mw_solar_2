import os

header_ui = """{% extends 'base.html' %}

{% block title %}Dashboard | MW Solar{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" x-data="dashboardData()">
    
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4" data-aos="fade-down">
        <div>
            <h1 class="text-3xl font-bold text-white tracking-tight">Dashboard Overview</h1>
            <p class="text-gray-400 mt-1">Monitor your solar investment and environmental impact.</p>
        </div>
        <div class="flex space-x-3">
            <button class="px-4 py-2 glass-panel rounded-lg text-sm font-medium text-gray-300 hover:text-white transition-colors border border-gray-700">
                <i class="fa-solid fa-download mr-2"></i> Export Report
            </button>
            <a href="{% url 'calculator' %}" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium text-white transition-colors shadow-lg shadow-blue-500/20">
                <i class="fa-solid fa-plus mr-2"></i> New Calculation
            </a>
        </div>
    </div>
"""

new_ui = """    {% if has_client and not force_show_calc %}
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
            <div class="relative w-full h-64"><canvas id="chartMonthlyGen"></canvas></div>
        </div>
        <!-- 2. Monthly Revenue (Bar) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Monthly Revenue</h3>
            <div class="relative w-full h-64"><canvas id="chartMonthlyRev"></canvas></div>
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
            <div class="relative w-full h-64"><canvas id="chartExportTrend"></canvas></div>
        </div>
        <!-- 6. Lifetime Prod (Area) -->
        <div class="glass-card rounded-2xl p-6">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Lifetime Production</h3>
            <div id="chartLifetimeProd" class="w-full h-64 flex justify-center items-center"></div>
        </div>
    </div>
"""

old_ui = """    {% elif latest_calc %}
    <!-- Top Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="glass-card rounded-2xl p-6 relative overflow-hidden group" data-aos="fade-up" data-aos-delay="100">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <i class="fa-solid fa-money-bill-wave text-6xl text-blue-500"></i>
            </div>
            <div class="relative z-10">
                <p class="text-sm font-medium text-gray-400 mb-1">Total Investment</p>
                <h3 class="text-3xl font-bold text-white">₹{{ latest_calc.investment|floatformat:0 }}</h3>
            </div>
        </div>
        <div class="glass-card rounded-2xl p-6 relative overflow-hidden group" data-aos="fade-up" data-aos-delay="200">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <i class="fa-solid fa-piggy-bank text-6xl text-emerald-500"></i>
            </div>
            <div class="relative z-10">
                <p class="text-sm font-medium text-gray-400 mb-1">20-Year Savings</p>
                <h3 class="text-3xl font-bold text-emerald-400">₹{{ latest_calc.twenty_year|floatformat:0 }}</h3>
            </div>
        </div>
        <div class="glass-card rounded-2xl p-6 relative overflow-hidden group" data-aos="fade-up" data-aos-delay="300">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <i class="fa-solid fa-wallet text-6xl text-purple-500"></i>
            </div>
            <div class="relative z-10">
                <p class="text-sm font-medium text-gray-400 mb-1">Net Profit</p>
                <h3 class="text-3xl font-bold text-white">₹{{ latest_calc.net_profit|floatformat:0 }}</h3>
            </div>
        </div>
        <div class="glass-card rounded-2xl p-6 relative overflow-hidden group" data-aos="fade-up" data-aos-delay="400">
            <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <i class="fa-solid fa-leaf text-6xl text-green-500"></i>
            </div>
            <div class="relative z-10">
                <p class="text-sm font-medium text-gray-400 mb-1">Carbon Saved (20y)</p>
                <h3 class="text-3xl font-bold text-green-400">{{ latest_calc.carbon_offset_20y|floatformat:1 }} Tons</h3>
            </div>
        </div>
    </div>
    
    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div class="glass-card rounded-2xl p-6" data-aos="fade-up" data-aos-delay="500">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Investment Growth Over Time</h3>
            <div id="chart-investment-growth" class="w-full h-64"></div>
        </div>
        <div class="glass-card rounded-2xl p-6" data-aos="fade-up" data-aos-delay="600">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Cumulative Savings Milestone</h3>
            <div class="relative w-full h-64">
                <canvas id="chartSavingsComparison"></canvas>
            </div>
        </div>
        <div class="glass-card rounded-2xl p-6" data-aos="fade-up" data-aos-delay="700">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Financial Breakdown</h3>
            <div id="chart-financial-breakdown" class="w-full h-64 flex justify-center items-center"></div>
        </div>
        <div class="glass-card rounded-2xl p-6" data-aos="fade-up" data-aos-delay="800">
            <h3 class="text-lg font-medium text-gray-200 mb-4">Return on Investment</h3>
            <div id="chart-roi-radial" class="w-full h-64 flex justify-center items-center"></div>
        </div>
    </div>
"""

empty_ui = """    {% else %}
    <div class="glass-card rounded-3xl p-12 text-center border border-gray-800" data-aos="zoom-in">
        <div class="w-20 h-20 mx-auto bg-gray-800 rounded-full flex items-center justify-center mb-6 shadow-inner">
            <i class="fa-solid fa-chart-simple text-3xl text-gray-500"></i>
        </div>
        <h2 class="text-2xl font-bold text-white mb-2">No calculations yet</h2>
        <p class="text-gray-400 mb-8 max-w-md mx-auto">Start your journey to clean energy. Calculate your potential solar savings now to unlock your personalized dashboard.</p>
        <a href="{% url 'calculator' %}" class="inline-flex items-center px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium transition-colors shadow-lg shadow-blue-500/20">
            <i class="fa-solid fa-calculator mr-2"></i> Calculate Savings Now
        </a>
    </div>
    {% endif %}

</div>
{% endblock %}
"""

js_scripts = """{% block extra_scripts %}
{% if has_client and not force_show_calc %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        fetch('/api/charts/')
            .then(response => response.json())
            .then(data => {
                new Chart(document.getElementById('chartMonthlyGen').getContext('2d'), {
                    type: 'line',
                    data: { labels: data.monthly_gen.labels, datasets: [{ label: 'Generation (kWh)', data: data.monthly_gen.data, borderColor: '#f59e0b', tension: 0.4, fill: true, backgroundColor: 'rgba(245, 158, 11, 0.1)' }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
                });

                new Chart(document.getElementById('chartMonthlyRev').getContext('2d'), {
                    type: 'bar',
                    data: { labels: data.monthly_revenue.labels, datasets: [{ label: 'Revenue (₹)', data: data.monthly_revenue.data, backgroundColor: '#10b981', borderRadius: 4 }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
                });

                new ApexCharts(document.querySelector("#chartInvestmentDist"), {
                    series: data.investment_dist.data, labels: data.investment_dist.labels,
                    chart: { type: 'pie', height: '100%', foreColor: '#9ca3af' }, colors: ['#3b82f6', '#8b5cf6'], stroke: { show: false }, legend: { position: 'bottom' }, tooltip: { theme: 'dark' }
                }).render();

                new ApexCharts(document.querySelector("#chartRevenueDist"), {
                    series: data.revenue_dist.data, labels: data.revenue_dist.labels,
                    chart: { type: 'pie', height: '100%', foreColor: '#9ca3af' }, colors: ['#10b981', '#ef4444', '#f59e0b'], stroke: { show: false }, legend: { position: 'bottom' }, tooltip: { theme: 'dark' }
                }).render();

                new Chart(document.getElementById('chartExportTrend').getContext('2d'), {
                    type: 'line',
                    data: { labels: data.export_trend.labels, datasets: [{ label: 'Exported (kWh)', data: data.export_trend.data, borderColor: '#3b82f6', tension: 0.1 }] },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
                });

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
{% elif latest_calc %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const data = {
            investment: parseFloat("{{ latest_calc.investment }}"),
            year1: parseFloat("{{ latest_calc.annual_savings }}"),
            year3: parseFloat("{{ latest_calc.three_year }}"),
            year5: parseFloat("{{ latest_calc.five_year }}"),
            year10: parseFloat("{{ latest_calc.ten_year }}"),
            year15: parseFloat("{{ latest_calc.fifteen_year }}"),
            year20: parseFloat("{{ latest_calc.twenty_year }}"),
            netProfit: parseFloat("{{ latest_calc.net_profit }}"),
            maintenance: parseFloat("{{ latest_calc.maintenance_cost }}"),
            roi: parseFloat("{{ latest_calc.roi }}"),
            breakEven: parseFloat("{{ latest_calc.break_even }}")
        };

        const areaOptions = {
            series: [{ name: 'Cumulative Savings', data: [0, data.year1, data.year3, data.year5, data.year10, data.year15, data.year20] }, 
                     { name: 'Investment Cost', data: [data.investment, data.investment, data.investment, data.investment, data.investment, data.investment, data.investment] }],
            chart: { type: 'area', height: '100%', parentHeightOffset: 0, toolbar: { show: false }, foreColor: '#9ca3af', animations: { enabled: true, easing: 'easeinout', speed: 800 } },
            colors: ['#8b5cf6', '#ef4444'],
            fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05, stops: [0, 90, 100] } },
            dataLabels: { enabled: false }, stroke: { curve: 'smooth', width: 2 },
            xaxis: { categories: ['Year 0', 'Year 1', 'Year 3', 'Year 5', 'Year 10', 'Year 15', 'Year 20'], axisBorder: { show: false }, axisTicks: { show: false } },
            yaxis: { labels: { formatter: (value) => { return "₹" + (value/1000).toFixed(0) + "k" } } },
            grid: { borderColor: 'rgba(255,255,255,0.05)', strokeDashArray: 4 },
            legend: { position: 'top', horizontalAlign: 'right' }, tooltip: { theme: 'dark' }
        };
        new ApexCharts(document.querySelector("#chart-investment-growth"), areaOptions).render();

        const ctxBar = document.getElementById('chartSavingsComparison').getContext('2d');
        new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: ['1 Year', '3 Years', '5 Years', '10 Years', '15 Years', '20 Years'],
                datasets: [{ label: 'Savings (₹)', data: [data.year1, data.year3, data.year5, data.year10, data.year15, data.year20], backgroundColor: 'rgba(59, 130, 246, 0.8)', borderRadius: 6, barPercentage: 0.6 }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.05)' } } } }
        });

        const donutOptions = {
            series: [data.netProfit, data.investment, data.maintenance],
            labels: ['Net Profit', 'Initial Investment', 'Maintenance (20y)'],
            chart: { type: 'donut', height: '100%', foreColor: '#9ca3af', animations: { speed: 1000 } },
            colors: ['#10b981', '#3b82f6', '#f59e0b'],
            plotOptions: { pie: { donut: { size: '75%', background: 'transparent' } } },
            dataLabels: { enabled: false }, stroke: { show: false }, legend: { position: 'bottom' }, tooltip: { theme: 'dark' }
        };
        new ApexCharts(document.querySelector("#chart-financial-breakdown"), donutOptions).render();

        const radialOptions = {
            series: [Math.min(data.roi, 1000)],
            chart: { type: 'radialBar', height: '100%', animations: { speed: 1500 } },
            plotOptions: { radialBar: { startAngle: -135, endAngle: 135, hollow: { size: '65%', background: 'transparent' }, track: { background: 'rgba(255,255,255,0.05)', strokeWidth: '100%' }, dataLabels: { name: { fontSize: '14px', color: '#9ca3af', offsetY: 20 }, value: { offsetY: -10, fontSize: '32px', color: '#fff', formatter: function (val) { return data.roi + "%"; } } } } },
            fill: { type: 'gradient', gradient: { shade: 'dark', type: 'horizontal', gradientToColors: ['#3b82f6'], stops: [0, 100] } }, stroke: { lineCap: 'round' }, colors: ['#8b5cf6'], labels: ['20-Year ROI'],
        };
        new ApexCharts(document.querySelector("#chart-roi-radial"), radialOptions).render();
    });
</script>
{% endif %}
{% endblock %}
"""

with open('templates/solar/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(header_ui + new_ui + old_ui + empty_ui + js_scripts)

print("Dashboard UI reverted to user preferred implementation")
