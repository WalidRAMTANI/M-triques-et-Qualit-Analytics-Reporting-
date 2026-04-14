import os
import sys
import importlib

sys.path.insert(0, os.path.abspath('.'))

errors = []
for f in os.listdir('app/routers'):
    if f.endswith('.py') and f != '__init__.py':
        module_name = f"app.routers.{f[:-3]}"
        try:
            importlib.import_module(module_name)
            print(f"{module_name}: OK")
        except Exception as e:
            errors.append((module_name, e))

if errors:
    print("\n--- ERRORS ---")
    for m, e in errors:
        print(f"{m}: {type(e).__name__} - {e}")
