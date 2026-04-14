import os
import re

def generate_pages():
    routers_dir = r"c:\Users\willi\Desktop\projetpython\M-triques-et-Qualit-Analytics-Reporting-\M-triques-et-Qualit-Analytics-Reporting-\app\routers"
    pages_dir = r"c:\Users\willi\Desktop\projetpython\M-triques-et-Qualit-Analytics-Reporting-\M-triques-et-Qualit-Analytics-Reporting-\gui\src\pages"
    
    # Exclude routers that already have pages
    exclude_routers = ['alerts.py', 'dashboard.py', 'metrics.py', 'sessions.py', 'aavs.py', '__init__.py']
    
    generated_pages = []

    for filename in os.listdir(routers_dir):
        if not filename.endswith('.py') or filename in exclude_routers:
            continue
        
        filepath = os.path.join(routers_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all routes
        # @router.get("/path")
        # def function_name(...):
        
        route_pattern = re.compile(r'@router\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"].*?\)\s*\n(?:@[^\n]+\n)*def\s+([a-zA-Z0-9_]+)\(', re.DOTALL)
        
        routes = route_pattern.findall(content)
        if not routes:
            continue
            
        module_name = filename[:-3]
        page_name = module_name.capitalize() + "Page"
        generated_pages.append((module_name, page_name))
        
        methods_ui = []
        for method, path, func_name in routes:
            # Extract path params like {id_aav}
            path_params = re.findall(r'\{([a-zA-Z0-9_]+)\}', path)
            
            # Simple form for each function
            method_col = f"""
    def build_{func_name}(self):
        output = ft.Text(size=12, selectable=True)
        inputs = {{}}"""
            
            for param in path_params:
                method_col += f"""
        inputs['{param}'] = ft.TextField(label="{param}", width=150, dense=True)"""
                
            method_col += f"""
        def on_click(e):
            final_path = "{path}" """
            
            for param in path_params:
                method_col += f"""
            if inputs['{param}'].value:
                final_path = final_path.replace("{{{param}}}", inputs['{param}'].value)"""
                
            method_col += f"""
            
            try:
                import httpx
                url = "http://localhost:8000" + final_path
                # Only generic mock execution for everything except simple GETs, simplified for UI
                r = httpx.request("{method.upper()}", url, timeout=5)
                try:
                    res = r.json()
                    import json
                    output.value = json.dumps(res, indent=2, ensure_ascii=False)
                except:
                    output.value = r.text
            except Exception as ex:
                output.value = f"Erreur: {{str(ex)}}"
            self._page.update()

        controls = [
            ft.Text("{method.upper()} {path} (Function: {func_name})", weight=ft.FontWeight.W_600),
            ft.Row([*inputs.values(), ft.ElevatedButton("Exécuter", on_click=on_click)]),
            ft.Container(output, bgcolor=ft.Colors.WHITE10, padding=10, border_radius=5)
        ]
        return ft.Container(content=ft.Column(controls), padding=10, border=ft.border.all(1, ft.Colors.WHITE24), border_radius=8, margin=ft.margin.only(bottom=10))
        """
            methods_ui.append(method_col)
            
        # Write page file
        page_content = f"""import flet as ft

class {page_name}:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None

    def build(self, page):
        self._page = page
        
        main_col = ft.Column([
            ft.Text("{module_name.capitalize()} Management", size=24, weight=ft.FontWeight.W_600),
            ft.Divider(),
        ], scroll=ft.ScrollMode.AUTO, expand=True)

""" + "\n".join(methods_ui) + f"""
        
        # Add all methods to main col
"""
        for _, _, func_name in routes:
            page_content += f"        main_col.controls.append(self.build_{func_name}())\n"
            
        page_content += "\n        return main_col\n"
        
        out_path = os.path.join(pages_dir, f"{module_name}_page.py")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(page_content)

    return generated_pages

pages = generate_pages()

# Update main.py
main_py_path = r"c:\Users\willi\Desktop\projetpython\M-triques-et-Qualit-Analytics-Reporting-\M-triques-et-Qualit-Analytics-Reporting-\gui\src\main.py"
with open(main_py_path, 'r', encoding='utf-8') as f:
    main_content = f.read()

# Add imports for these pages
imports = ""
for module, cls in pages:
    imports += f"from pages.{module}_page import {cls}\n"

main_content = imports + main_content

# Add callbacks in main.py
callbacks = ""
for module, cls in pages:
    callbacks += f"""
    def show_{module}(e=None):
        page_inst = {cls}(content_area)
        _set(page_inst.build(page))
"""

if "# ── Page callbacks" in main_content:
    main_content = main_content.replace("# ── Page callbacks ────────────────────────────────────────────────────────", "# ── Page callbacks ────────────────────────────────────────────────────────\n" + callbacks)

with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(main_content)

# Update sidebar.py
sidebar_py_path = r"c:\Users\willi\Desktop\projetpython\M-triques-et-Qualit-Analytics-Reporting-\M-triques-et-Qualit-Analytics-Reporting-\gui\src\pages\sidebar.py"
with open(sidebar_py_path, 'r', encoding='utf-8') as f:
    sidebar_content = f.read()
    
# Remove old advanced features block if present
import re
sidebar_content = re.sub(r'# Advanced Features.*?(?=# Project Info Section)', '', sidebar_content, flags=re.DOTALL)

buttons = """
                    # Auto-generated Routers Buttons
                    ft.Text("Fonctions", size=12, weight=ft.FontWeight.W_600, color="#E0E0E0"),
"""
for module, cls in pages:
    buttons += f"""
                    ft.TextButton("{module.capitalize()}", icon=ft.Icons.API, on_click=self.show_{module}),"""
                    
buttons += "\n                    ft.Divider(height=20),\n\n                    "

sidebar_content = sidebar_content.replace("# Project Info Section", buttons + "# Project Info Section")

# Also need to inject show_{module} into Sidebar constructor
init_args = ""
init_assign = ""
for module, cls in pages:
    init_args += f", show_{module}_cb=None"
    init_assign += f"\n        self.show_{module} = show_{module}_cb"
    
sidebar_content = sidebar_content.replace("show_sessions_cb=None,", f"show_sessions_cb=None{init_args}")
sidebar_content = sidebar_content.replace("self.show_sessions = show_sessions_cb", f"self.show_sessions = show_sessions_cb{init_assign}")

with open(sidebar_py_path, 'w', encoding='utf-8') as f:
    f.write(sidebar_content)
    
# Finally update main.py sidebar instantiation
sidebar_inst = "sidebar = Sidebar(\n"
sidebar_inst += "        show_alerts_cb     = show_alerts,\n"
sidebar_inst += "        show_about_cb      = show_about,\n"
sidebar_inst += "        show_aav_detail_cb = show_aav_detail,\n"
sidebar_inst += "        show_dashboard_cb  = show_dashboard,\n"
sidebar_inst += "        show_metrics_cb    = show_metrics,\n"
sidebar_inst += "        show_sessions_cb   = show_sessions,\n"
for module, cls in pages:
    sidebar_inst += f"        show_{module}_cb = show_{module},\n"
sidebar_inst += "    )"
    
# Replace the old sidebar instantiation
main_content = re.sub(r'sidebar = Sidebar\(.*?\)', sidebar_inst, main_content, flags=re.DOTALL)
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(main_content)

print(f"Generated {len(pages)} pages!")
