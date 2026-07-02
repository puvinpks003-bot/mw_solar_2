import re

with open('templates/solar/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix chartMonthlyGen
content = content.replace(
    '<canvas id="chartMonthlyGen" class="w-full h-64"></canvas>',
    '<div class="relative w-full h-64"><canvas id="chartMonthlyGen"></canvas></div>'
)

# Fix chartMonthlyRev
content = content.replace(
    '<canvas id="chartMonthlyRev" class="w-full h-64"></canvas>',
    '<div class="relative w-full h-64"><canvas id="chartMonthlyRev"></canvas></div>'
)

# Fix chartExportTrend
content = content.replace(
    '<canvas id="chartExportTrend" class="w-full h-64"></canvas>',
    '<div class="relative w-full h-64"><canvas id="chartExportTrend"></canvas></div>'
)

with open('templates/solar/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Canvas tags wrapped successfully.")
