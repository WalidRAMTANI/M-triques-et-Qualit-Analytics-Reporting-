import sys
from pathlib import Path

# Ajouter le chemin vers gui/src pour trouver les bonnes pages
GUI_SRC = Path(__file__).resolve().parent / "gui" / "src"
if str(GUI_SRC) not in sys.path:
    sys.path.insert(0, str(GUI_SRC))

# Ajouter la racine du projet pour les imports 'app'
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft
from main import main as flet_main

if __name__ == "__main__":
    # Lancement de l'application refactorisée
    ft.app(target=flet_main)
