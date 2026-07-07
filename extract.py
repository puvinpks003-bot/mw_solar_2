import os

source_file = 'templates/solar/dashboard.html'
dest_file = 'templates/solar/includes/dashboard_content.html'

with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if '<div id="dashboard-wrapper"' in line:
        start_idx = i
        break

if start_idx != -1:
    script_start = -1
    script_end = -1
    for i, line in enumerate(lines):
        if '<script>' in line:
            script_start = i
        if '</script>' in line:
            script_end = i

    # The end of the wrapper is at line 390 (index 389)
    # But since line numbers change, let's find it. It's the `</div>` before `{% endif %}` which is before `{% endblock %}`
    end_idx = -1
    for i in range(len(lines)):
        if '{% endblock %}' in lines[i]:
            # The div ends somewhere before this
            for j in range(i-1, -1, -1):
                if '</div>' in lines[j]:
                    end_idx = j
                    break
            break

    # wait, the file has {% endif %} on line 391
    content_lines = lines[start_idx:391] + ['\n'] + lines[script_start:script_end+1]
    content = ''.join(content_lines)

    os.makedirs('templates/solar/includes', exist_ok=True)
    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write(content)

    new_dashboard = ''.join(lines[:start_idx]) + '    {% include "solar/includes/dashboard_content.html" %}\n{% endblock %}\n'
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(new_dashboard)

    print('Successfully extracted dashboard_content.html')
else:
    print('Failed to find start_idx')
