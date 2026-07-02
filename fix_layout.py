import re

with open('templates/solar/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# I want to hide the original Top Stats Cards and Charts if has_client is true.
# The original block starts with <!-- Top Stats Cards --> and ends before {% else %} (which is the "No calculations yet" block).

# Let's change the logic at the top of the file:
# From:
# {% if has_client or latest_calc %}
#
# {% if has_client %}
# ... new UI ...
# {% endif %}
# <!-- Top Stats Cards -->
# ... old UI ...
# {% else %}
#
# To:
# {% if has_client %}
# ... new UI ...
# {% elif latest_calc %}
# <!-- Top Stats Cards -->
# ... old UI ...
# {% else %}

content = content.replace('{% if has_client or latest_calc %}', '')

content = content.replace('{% if has_client %}', '{% if has_client %}')

content = content.replace('<!-- Top Stats Cards -->', '{% elif latest_calc %}\n    <!-- Top Stats Cards -->', 1)

with open('templates/solar/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
