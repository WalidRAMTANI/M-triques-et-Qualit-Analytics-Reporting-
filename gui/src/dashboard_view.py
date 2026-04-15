"""
Dashboard view — consomme l'API REST via HTTP (httpx).
Endpoint principal : GET /dashboard/teachers/{id}/overview
"""

import sys
import base64
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft
import httpx

BASE_URL = "http://localhost:8000"


def api_get(path: str):
    """HTTP GET vers l'API, retourne le JSON ou None."""
    try:
        r = httpx.get(f"{BASE_URL}{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"[API GET] {path} → {e}")
        return None


def api_post(path: str, payload: dict):
    """HTTP POST vers l'API, retourne le JSON ou None."""
    try:
        r = httpx.post(f"{BASE_URL}{path}", json=payload, timeout=10)
        if r.status_code in (200, 201):
            return r.json()
        print(f"[API POST] {path} → {r.status_code}: {r.text}")
        return None
    except Exception as e:
        print(f"[API POST] {path} → {e}")
        return None


def create_dashboard_view(page: ft.Page):
    """Factory function pour la vue dashboard utilisée par main.py."""
    COLOR_PRIMARY = "#1565C0"
    COLOR_BG_INPUT = "#E3F2FD"

    champ_recherche = ft.TextField(
        label="ID Enseignant (ex: 1)",
        width=300,
        border_radius=10,
        bgcolor=COLOR_BG_INPUT,
        prefix_icon=ft.Icons.PERSON_SEARCH,
    )

    container_stats = ft.Row(wrap=True, spacing=30, alignment=ft.MainAxisAlignment.CENTER)
    text_info = ft.Text("Entrez un ID pour voir les statistiques", size=16, italic=True, color="#666666")

    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=40),
                ft.Text(str(value), size=32, weight="bold", color="black"),
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
            stats = api_get(f"/dashboard/teachers/{target_id}/overview")

            container_stats.controls.clear()
            if stats:
                container_stats.controls.append(create_stat_card("AAV Gérés", stats.get("aavs_geres", 0), ft.Icons.AUTO_GRAPH, COLOR_PRIMARY))
                container_stats.controls.append(create_stat_card("Apprenants", stats.get("apprenants_total", 0), ft.Icons.PEOPLE, "#4CAF50"))
                taux = stats.get("taux_succes_moyen", 0)
                container_stats.controls.append(create_stat_card("Succès Moyen", f"{taux * 100:.1f}%", ft.Icons.CHECK_CIRCLE, "#FF9800"))
                container_stats.controls.append(create_stat_card("Alertes Actives", stats.get("alertes_actives", 0), ft.Icons.NOTIFICATIONS_ACTIVE, "#F44336"))
                text_info.value = f"Statistiques pour : {stats.get('nom', f'Enseignant #{target_id}')}"
                text_info.italic = False
                text_info.color = "black"
            else:
                text_info.value = f"Aucun enseignant trouvé pour l'ID {target_id}"
                text_info.color = "red"
            page.update()
        except Exception as err:
            container_stats.controls.clear()
            text_info.value = f"Erreur : {err}"
            text_info.color = "red"
            page.update()

    def telecharger_pdf(e):
        try:
            payload = {"type_rapport": "discipline", "id_cible": "Programmation", "format": "pdf"}
            rapport = api_post("/reports/generate", payload)
            if rapport and rapport.get("contenu"):
                import base64
                from pathlib import Path
                
                export_dir = PROJECT_ROOT / "exports"
                export_dir.mkdir(exist_ok=True)
                filename = export_dir / "Rapport_Global_Dashboard.pdf"
                
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(rapport["contenu"]))
                
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Rapport exporté dans : {filename}"), bgcolor="green")
                page.snack_bar.open = True
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Impossible de générer le rapport PDF."), bgcolor="red")
                page.snack_bar.open = True
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"⚠️ Erreur PDF : {err}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    header = ft.Column([
        ft.Text("Tableau de Bord Pédagogique", size=40, weight="bold", color=COLOR_PRIMARY),
        ft.Text("Suivi en temps réel de la performance des AAV", size=18, color="#666666"),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    view = ft.Container(
        content=ft.Column([
            header,
            ft.Divider(height=30, color="transparent"),
            ft.Row([
                champ_recherche,
                ft.ElevatedButton("Charger", icon=ft.Icons.REFRESH, on_click=charger_donnees, bgcolor=COLOR_PRIMARY, color="white", height=50),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
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
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
        padding=40,
        expand=True,
    )

    return view


def main(page: ft.Page):
    """Standalone entry point."""
    page.title = "Test Dashboard View"
    page.bgcolor = "#F5F5F5"
    page.add(create_dashboard_view(page))


if __name__ == "__main__":
    ft.app(target=main)
