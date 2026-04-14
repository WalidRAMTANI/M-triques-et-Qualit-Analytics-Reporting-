import sys
import os
import base64
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2] 
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft
from app.routers import dashboard, reports
from app.model.schemas import RapportRequest

def main(page: ft.Page):
    page.title = "Tableau de Bord Pédagogique"
    page.padding = 40
    page.bgcolor = "#F5F5F5"
    page.window_width = 1000
    page.window_height = 800
    
    # Correction alignement page
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    COLOR_PRIMARY = "#1565C0"
    COLOR_BG_INPUT = "#E3F2FD"

    # --- ÉLÉMENTS UI ---
    champ_recherche = ft.TextField(
        label="ID Enseignant (ex: 1)", 
        width=300,
        border_radius=10,
        bgcolor=COLOR_BG_INPUT,
        prefix_icon=ft.Icons.PERSON_SEARCH,
    )
    
    container_stats = ft.Row(wrap=True, spacing=30, alignment=ft.MainAxisAlignment.CENTER)
    
    text_info = ft.Text("Entrez un ID pour voir les statistiques", size=16, italic=True, color="gray")

    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=40),
                ft.Text(value, size=32, weight="bold", color="black"),
                ft.Text(title, size=16, color="gray", weight="w500"),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=220,
            height=180,
            bgcolor="white",
            border_radius=20,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
        )

    def charger_donnees(e=None):
        if not champ_recherche.value:
            return
        try:
            target_id = int(champ_recherche.value)
            stats = dashboard.get_teacher_dashboard(target_id)
            
            container_stats.controls.clear()
            container_stats.controls.append(create_stat_card("AAV Gérés", str(stats.aavs_geres), ft.Icons.AUTO_GRAPH, COLOR_PRIMARY))
            container_stats.controls.append(create_stat_card("Apprenants", str(stats.apprenants_total), ft.Icons.PEOPLE, "#4CAF50"))
            container_stats.controls.append(create_stat_card("Succès Moyen", f"{stats.taux_succes_moyen*100:.1f}%", ft.Icons.CHECK_CIRCLE, "#FF9800"))
            container_stats.controls.append(create_stat_card("Alertes Actives", str(stats.alertes_actives), ft.Icons.NOTIFICATIONS_ACTIVE, "#F44336"))
            
            text_info.value = f"Statistiques pour : {stats.nom}"
            text_info.italic = False
            text_info.color = "black"
            page.update()
        except Exception as err:
            print(f"ERREUR DASHBOARD (ID {champ_recherche.value}) : {err}")
            container_stats.controls.clear()
            text_info.value = f"Aucun enseignant trouvé pour l'ID {champ_recherche.value}"
            text_info.color = "red"
            page.update()

    def telecharger_pdf(e):
        try:
            request = RapportRequest(type_rapport="discipline", id_cible="Informatique", format="pdf")
            rapport = reports.generate_rapport_personnalise(request)
            pdf_bytes = base64.b64decode(json.loads(rapport.contenu))

            export_path = Path("exports")
            export_path.mkdir(exist_ok=True)
            filename = export_path / "rapport_global.pdf"
            
            with open(filename, "wb") as f:
                f.write(pdf_bytes)
                
            page.snack_bar = ft.SnackBar(ft.Text(f"Rapport exporté : {filename}"))
            page.snack_bar.open = True
            page.update()
        except Exception as err:
            print(f"Erreur Export: {err}")

    # --- LAYOUT PRINCIPAL ---
    header = ft.Column([
        ft.Text("Tableau de Bord Pédagogique", size=40, weight="bold", color=COLOR_PRIMARY),
        ft.Text("Suivi en temps réel de la performance des AAV", size=18, color="gray"),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    search_bar = ft.Row([
        champ_recherche,
        ft.ElevatedButton("Charger", icon=ft.Icons.REFRESH, on_click=charger_donnees, bgcolor=COLOR_PRIMARY, color="white", height=50),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    page.add(
        ft.Column([
            header,
            ft.Divider(height=30, color="transparent"),
            search_bar,
            ft.Divider(height=40, color="transparent"),
            text_info,
            ft.Divider(height=20, color="transparent"),
            container_stats,
            ft.Divider(height=60, color="transparent"),
            ft.ElevatedButton(
                "Télécharger Rapport Global PDF", 
                icon=ft.Icons.PICTURE_AS_PDF, 
                on_click=telecharger_pdf,
                bgcolor=COLOR_PRIMARY,
                color="white",
                height=55,
                width=300
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
    )

    # Chargement initial
    champ_recherche.value = "1"
    charger_donnees()

if __name__ == "__main__":
    ft.app(target=main)
