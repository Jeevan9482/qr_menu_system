import os
import re

FILES = [
    r"templates\owner\tables.html",
    r"templates\owner\categories.html",
    r"templates\owner\items.html",
    r"templates\orders\history\completed_orders.html",
    r"templates\owner\draft_list.html",
    r"templates\owner\draft_billing.html",
    r"templates\owner\report_detail.html",
    r"templates\owner\reports.html",
    r"templates\owner\bill_receipt.html",
    r"templates\owner\billing.html",
    r"templates\orders\owner_orders.html",
    r"templates\inventory\manage_recipes.html",
    r"templates\inventory\dashboard.html",
]

BASE_DIR = r"c:\JEEVAN\Times Point Technologies Pvt Ltd\Restnon\qr_menu_system"

# Map filename to the active key
FILE_TO_ACTIVE = {
    "tables.html": "tables",
    "categories.html": "categories",
    "items.html": "items",
    "completed_orders.html": "history",
    "draft_list.html": "draft",
    "draft_billing.html": "draft",
    "report_detail.html": "reports",
    "reports.html": "reports",
    "bill_receipt.html": "pos",
    "billing.html": "pos",
    "owner_orders.html": "dashboard", # assuming owner_orders is the dashboard
    "dashboard.html": "inventory",
    "manage_recipes.html": "inventory",
}

SIDEBAR_TEMPLATE = """<ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link {active_dashboard}" href="{% url 'owner_orders' %}">
                            <i class="fas fa-home"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_pos}" href="{% url 'owner_billing' %}">
                            <i class="fas fa-cash-register"></i> Bill / POS
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_draft}" href="{% url 'draft_list' %}">
                            <i class="fas fa-file-invoice"></i> Draft Bills
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_reports}" href="{% url 'owner_reports' %}">
                            <i class="fas fa-chart-line"></i> Reports
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_tables}" href="/owner/tables/">
                            <i class="fas fa-chair"></i> Table Management
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_categories}" href="/menu/owner/categories/">
                            <i class="fas fa-folder-open"></i> Category Management
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_items}" href="{% url 'owner_items' %}">
                            <i class="fas fa-utensils"></i> Menu Items
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_history}" href="/orders/history/">
                            <i class="fas fa-history"></i> Order History
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_kitchen}" href="{% url 'kitchen_display' %}" target="_blank">
                            <i class="fas fa-fire-burner"></i> Kitchen Display
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {active_inventory}" href="/inventory/">
                            <i class="fas fa-boxes"></i> Inventory
                            {% if global_low_stock_count > 0 %}
                                <span class="badge bg-danger ms-auto rounded-pill" style="font-size: 0.7rem;">{{ global_low_stock_count }}</span>
                            {% endif %}
                        </a>
                    </li>
                    <div class="nav-divider"></div>
                    <li class="nav-item">
                        <a class="nav-link logout" href="/logout/">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </a>
                    </li>
                </ul>"""

for rel_path in FILES:
    filepath = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, not found")
        continue

    filename = os.path.basename(filepath)
    active_key = FILE_TO_ACTIVE.get(filename, "")

    # build kwargs
    kwargs = {
        "active_dashboard": "active" if active_key == "dashboard" else "",
        "active_pos": "active" if active_key == "pos" else "",
        "active_draft": "active" if active_key == "draft" else "",
        "active_reports": "active" if active_key == "reports" else "",
        "active_tables": "active" if active_key == "tables" else "",
        "active_categories": "active" if active_key == "categories" else "",
        "active_items": "active" if active_key == "items" else "",
        "active_history": "active" if active_key == "history" else "",
        "active_kitchen": "active" if active_key == "kitchen" else "",
        "active_inventory": "active" if active_key == "inventory" else "",
    }

    # Clean empty {active_xxx} rendering to avoid trailing spaces in class="nav-link "
    # But wait, we can just let Python format do it, and replace 'class="nav-link "' to 'class="nav-link"'
    rendered_sidebar = SIDEBAR_TEMPLATE
    for k, v in kwargs.items():
        rendered_sidebar = rendered_sidebar.replace('{' + k + '}', v)
    rendered_sidebar = rendered_sidebar.replace('class="nav-link "', 'class="nav-link"')

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # ensure CSS is updated properly
    def css_replacer(m):
        block = m.group(0)
        # remove existing overflow-y
        block = re.sub(r'overflow-y:\s*auto;\s*', '', block)
        # ensure min-height is replaced with height
        if 'min-height: 100vh;' in block:
            block = block.replace('min-height: 100vh;', 'height: 100vh;\n            overflow-y: auto;')
        elif 'height: 100vh;' in block and 'overflow-y: auto;' not in block:
            # Maybe the previous run changed min-height to height, so we ensure overflow is there
            block = block.replace('height: 100vh;', 'height: 100vh;\n            overflow-y: auto;')
        return block
        
    content = re.sub(r'\.sidebar\s*\{[^}]*\}', css_replacer, content)

    # replace exactly the <ul class="nav flex-column">...</ul>
    ul_pattern = re.compile(r'<ul\s+class="nav flex-column">.*?</ul>', re.DOTALL)
    new_content = ul_pattern.sub(rendered_sidebar, content)

    # Add Top Nav for notifications right after Main Content opens, ONLY if it doesn't exist
    top_nav_html = """
                <!-- GLOBAL TOP NAV -->
                <div class="d-flex justify-content-end align-items-center mb-4 pb-2 border-bottom">
                    <div class="dropdown">
                        <button class="btn btn-light position-relative" type="button" id="notificationDropdown" data-bs-toggle="dropdown" aria-expanded="false" style="border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center;">
                            <i class="fas fa-bell fs-5 text-secondary"></i>
                            {% if global_low_stock_count > 0 %}
                            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger shadow-sm border border-white">
                                {{ global_low_stock_count }}
                                <span class="visually-hidden">unread messages</span>
                            </span>
                            {% endif %}
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end shadow-lg border-0 mt-2" aria-labelledby="notificationDropdown" style="width: 320px; border-radius: 12px; overflow: hidden;">
                            <li class="px-3 py-2 bg-light border-bottom fw-bold text-muted" style="font-size: 0.85rem; letter-spacing: 0.5px;">NOTIFICATIONS</li>
                            {% if global_low_stock_count > 0 %}
                                {% for item in global_low_stock_items|slice:":5" %}
                                <li>
                                    <a class="dropdown-item py-3 border-bottom d-flex align-items-start gap-3 flex-wrap text-wrap text-break" href="{% url 'inventory_dashboard' %}" style="white-space: normal;">
                                        <div class="rounded-circle bg-danger bg-opacity-10 text-danger d-flex align-items-center justify-content-center flex-shrink-0" style="width: 35px; height: 35px;">
                                            <i class="fas fa-exclamation-triangle"></i>
                                        </div>
                                        <div>
                                            <strong class="d-block text-dark">{{ item.name }}</strong>
                                            <span class="text-danger small">Stock Low: {{ item.quantity }} {{ item.get_unit_display }}</span>
                                        </div>
                                    </a>
                                </li>
                                {% endfor %}
                                <li><a class="dropdown-item text-center py-2 text-primary fw-bold" href="{% url 'inventory_dashboard' %}" style="font-size: 0.9rem;">View All in Inventory &rarr;</a></li>
                            {% else %}
                                <li><div class="dropdown-item py-4 text-center text-muted"><i class="fas fa-check-circle fs-3 text-success mb-2 d-block"></i> <span class="d-block">All systems go!</span><span class="small d-block opacity-75">No immediate alerts</span></div></li>
                            {% endif %}
                        </ul>
                    </div>
                </div>
                """
    
    if "GLOBAL TOP NAV" not in new_content:
        # We need to find the opening <div class="col-md-9 main-content"> and insert immediately after
        main_content_pattern = re.compile(r'(<div\s+class="col-md-9\s+main-content"[^>]*>)')
        new_content = main_content_pattern.sub(r'\1\n' + top_nav_html, new_content)
    else:
        # If it DOES exist, replace it to ensure it's up to date
        top_nav_pattern = re.compile(r'<!-- GLOBAL TOP NAV -->.*?</div>\s*</div>\s*</div>', re.DOTALL)
        new_content = top_nav_pattern.sub(top_nav_html.strip(), new_content)

    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Processed {filepath}")
