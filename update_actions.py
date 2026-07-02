import re

# 1. Update urls.py
with open('solar/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

urls_content = urls_content.replace(
    "path('history/', views.history_view, name='history'),",
    "path('history/', views.history_view, name='history'),\n    path('history/delete/<int:calc_id>/', views.delete_calculation_view, name='delete_calculation'),"
)

with open('solar/urls.py', 'w', encoding='utf-8') as f:
    f.write(urls_content)

# 2. Update dashboard.html
with open('templates/solar/dashboard.html', 'r', encoding='utf-8') as f:
    dashboard_content = f.read()

dashboard_content = dashboard_content.replace(
    "{% if has_client %}",
    "{% if has_client and not force_show_calc %}"
)

with open('templates/solar/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_content)

# 3. Update history.html actions
with open('templates/solar/history.html', 'r', encoding='utf-8') as f:
    history_content = f.read()

old_actions = """                        <td class="px-6 py-4 text-right">
                            <button class="text-gray-500 hover:text-white transition-colors mr-3" title="View Details">
                                <i class="fa-solid fa-eye"></i>
                            </button>
                            <button class="text-gray-500 hover:text-red-400 transition-colors" title="Delete">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>"""

new_actions = """                        <td class="px-6 py-4 text-right">
                            <a href="{% url 'dashboard' %}?calc_id={{ calc.id }}" class="text-gray-500 hover:text-white transition-colors mr-3" title="View Details">
                                <i class="fa-solid fa-eye"></i>
                            </a>
                            <form action="{% url 'delete_calculation' calc.id %}" method="POST" class="inline" onsubmit="return confirm('Are you sure you want to delete this calculation?');">
                                {% csrf_token %}
                                <button type="submit" class="text-gray-500 hover:text-red-400 transition-colors" title="Delete">
                                    <i class="fa-solid fa-trash"></i>
                                </button>
                            </form>
                        </td>"""

history_content = history_content.replace(old_actions, new_actions)

with open('templates/solar/history.html', 'w', encoding='utf-8') as f:
    f.write(history_content)

print("Updated urls and templates")
