import re

with open('templates/solar/history.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the table opening tag to add an ID
content = content.replace('<table class="w-full text-left border-collapse">', '<table id="historyTable" class="w-full text-left border-collapse">')

# Remove the manual pagination placeholder because DataTables adds its own
pagination_html = """        <!-- Pagination placeholder -->
        <div class="bg-gray-900/30 px-6 py-4 border-t border-gray-800 flex items-center justify-between">
            <p class="text-sm text-gray-400">Showing <span class="font-medium text-white">{{ calculations|length }}</span> results</p>
            <div class="flex space-x-2">
                <button class="px-3 py-1 rounded border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 disabled:opacity-50" disabled>Previous</button>
                <button class="px-3 py-1 rounded border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 disabled:opacity-50" disabled>Next</button>
            </div>
        </div>"""
content = content.replace(pagination_html, '')

# Add the DataTables CSS, JS, and initialization at the bottom inside {% block extra_scripts %}
# Wait, history.html doesn't have {% block extra_scripts %} yet. I'll append it before {% endblock %} content, or wait, I should append it properly.
# The base.html has {% block extra_scripts %} (I assume, since dashboard used it).
# Let's check where {% endblock %} is for content.
# It's at the very end.

scripts_block = """
{% endblock %}

{% block extra_scripts %}
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<style>
    /* Dark mode overrides for DataTables */
    .dataTables_wrapper .dataTables_length, .dataTables_wrapper .dataTables_filter, .dataTables_wrapper .dataTables_info, .dataTables_wrapper .dataTables_processing, .dataTables_wrapper .dataTables_paginate {
        color: #9ca3af !important;
        margin-bottom: 1rem;
        margin-top: 1rem;
        padding: 0 1.5rem;
    }
    .dataTables_wrapper .dataTables_length select {
        background-color: #1f2937;
        border: 1px solid #374151;
        color: white;
        border-radius: 0.375rem;
        padding: 0.25rem 0.5rem;
    }
    .dataTables_wrapper .dataTables_filter input {
        background-color: #1f2937;
        border: 1px solid #374151;
        color: white;
        border-radius: 0.375rem;
        padding: 0.25rem 0.75rem;
        margin-left: 0.5rem;
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button {
        color: #9ca3af !important;
        border: 1px solid #374151 !important;
        background: #1f2937 !important;
        border-radius: 0.375rem;
        margin-left: 0.25rem;
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button.current, .dataTables_wrapper .dataTables_paginate .paginate_button.current:hover {
        color: white !important;
        background: #3b82f6 !important;
        border-color: #3b82f6 !important;
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button:hover {
        color: white !important;
        background: #374151 !important;
        border-color: #4b5563 !important;
    }
    table.dataTable.no-footer {
        border-bottom: 1px solid #1f2937;
    }
    table.dataTable thead th, table.dataTable thead td {
        border-bottom: 1px solid #1f2937;
    }
</style>
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script>
    $(document.ready(function() {
        $('#historyTable').DataTable({
            "pageLength": 10,
            "ordering": true,
            "info": true,
            "searching": true,
            "lengthChange": true,
            "language": {
                "search": "Filter records:",
                "lengthMenu": "Show _MENU_ entries per page"
            }
        });
    });
</script>
{% endblock %}
"""

# wait, there's a typo in jQuery: $(document.ready should be $(document).ready
scripts_block = scripts_block.replace('$(document.ready', '$(document).ready')

# Replace the closing {% endblock %} with the new block structure
content = content.replace('{% endblock %}', scripts_block)

with open('templates/solar/history.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added DataTables to history.html")
