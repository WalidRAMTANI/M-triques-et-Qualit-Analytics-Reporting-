"""
Metrics view — consomme l'API REST via HTTP (httpx).
Endpoints : GET/POST /metrics/aav/*, POST /reports/generate
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


def _get(path: str):
    try:
        r = httpx.get(f"{BASE_URL}{path}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"[GET] {path} → {e}")
        return None


def _post(path: str, payload: dict = None):
    try:
        r = httpx.post(f"{BASE_URL}{path}", json=payload or {}, timeout=10)
        return r.json() if r.status_code in (200, 201) else None
    except Exception as e:
        print(f"[POST] {path} → {e}")
        return None


def create_metrics_view(page: ft.Page):
    COLOR_PRIMARY = "#1565C0"
    COLOR_BG_INPUT = "#E3F2FD"
    COLOR_BORDER_INPUT = "#2196F3"
    COLOR_TEXT_RESULT = "#212121"

    champ_chiffre = ft.TextField(
        label="Numéro AAV",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        border_color=COLOR_BORDER_INPUT,
        bgcolor=COLOR_BG_INPUT,
        prefix_icon=ft.Icons.SEARCH,
        cursor_color=COLOR_PRIMARY,
    )

    affichage_resultat = ft.Text("Résultat : aucun", size=18, color=COLOR_TEXT_RESULT)

    def donne_get_metric(id_aav=None):
        target_id = id_aav if id_aav else (int(champ_chiffre.value) if champ_chiffre.value else None)
        if not target_id:
            return

        res = _get(f"/metrics/aav/{target_id}")
        if res:
            affichage_resultat.value = (
                f"METRIQUES POUR L'AAV #{res.get('id_aav', target_id)}\n"
                f"{'─' * 40}\n"
                f"Couverture ressources : {res.get('score_covering_ressources', 0)*100:.1f}%\n"
                f"Taux de succès moyen : {res.get('taux_succes_moyen', 0)*100:.1f}%\n"
                f"Est utilisable : {'OUI' if res.get('est_utilisable') else 'NON'}\n"
                f"Tentatives totales : {res.get('nb_tentatives_total', 0)}\n"
                f"Apprenants distincts : {res.get('nb_apprenants_distincts', 0)}\n"
                f"Ecart-type scores : {res.get('ecart_type_scores', 0):.3f}\n"
                f"Date de calcul : {res.get('date_calcul', 'N/A')}\n"
            )
            affichage_resultat.color = COLOR_TEXT_RESULT
            if not id_aav:
                champ_chiffre.value = str(target_id)
        else:
            affichage_resultat.value = f"Aucune métrique pour l'AAV {target_id} (calculez d'abord)"
            affichage_resultat.color = ft.Colors.RED_700
        page.update()

    def ouvrir_popup_toutes_metrics(e):
        try:
            res_list = _get("/metrics/aav/")

            def selectionner_aav(id_v):
                donne_get_metric(id_v)
                dialog.open = False
                page.update()

            items_list = []
            if res_list:
                for m in res_list:
                    items_list.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.ANALYTICS, color=COLOR_PRIMARY),
                            title=ft.Text(f"AAV #{m.get('id_aav', '?')}", weight="bold"),
                            subtitle=ft.Text(f"Succès: {m.get('taux_succes_moyen', 0)*100:.1f}% | Tentatives: {m.get('nb_tentatives_total', 0)}"),
                            on_click=lambda e, id_v=m.get('id_aav'): selectionner_aav(id_v)
                        )
                    )
            else:
                items_list = [ft.Text("Aucune métrique disponible.", italic=True)]

            dialog = ft.AlertDialog(
                title=ft.Text("Liste de toutes les Métriques"),
                content=ft.Container(
                    content=ft.ListView(items_list, spacing=10, padding=10),
                    width=500, height=400
                ),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or page.update())]
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        except Exception as err:
            print(f"ERREUR LISTE POPUP : {err}")

    def ouvrir_popup_historique(e):
        if not champ_chiffre.value:
            return
        try:
            id_actuel = int(champ_chiffre.value)
            hist = _get(f"/metrics/aav/{id_actuel}/history")
            items_list = []
            if hist:
                for h in hist:
                    date_str = str(h.get('date_calcul', '?'))[:16]
                    items_list.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.TIMELINE, color=ft.Colors.AMBER_700),
                            title=ft.Text(f"Calcul du {date_str}"),
                            subtitle=ft.Text(f"Succès: {h.get('taux_succes_moyen', 0)*100:.1f}% | Util: {'Oui' if h.get('est_utilisable') else 'Non'}"),
                        )
                    )
            else:
                items_list = [ft.Text("Aucun historique.", italic=True)]

            dialog = ft.AlertDialog(
                title=ft.Text(f"Historique AAV #{id_actuel}"),
                content=ft.Container(
                    content=ft.ListView(items_list, spacing=10, padding=10),
                    width=500, height=400
                ),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or page.update())]
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        except Exception as err:
            print(f"Erreur Historique: {err}")

    def lancer_calcul(e):
        if not champ_chiffre.value:
            return
        try:
            affichage_resultat.value = "Calcul en cours..."
            page.update()
            res = _post(f"/metrics/aav/{int(champ_chiffre.value)}/calculate")
            donne_get_metric()
        except Exception as err:
            affichage_resultat.value = f"Erreur calcul : {err}"
            affichage_resultat.color = ft.Colors.RED_700
            page.update()

    def telecharger_pdf(e):
        if not champ_chiffre.value:
            return
        try:
            target_id = int(champ_chiffre.value)
            payload = {"type_rapport": "aav", "id_cible": target_id, "format": "pdf"}
            rapport = _post("/reports/generate", payload)
            if rapport and rapport.get("contenu"):
                raw_content = json.loads(rapport["contenu"])
                pdf_bytes = base64.b64decode(raw_content)
                export_path = Path("exports")
                export_path.mkdir(exist_ok=True)
                filename = export_path / f"rapport_aav_{target_id}.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_bytes)
                page.snack_bar = ft.SnackBar(ft.Text(f"Rapport enregistré : {filename}"))
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Erreur génération PDF."))
            page.snack_bar.open = True
            page.update()
        except Exception as err:
            print(f"Erreur PDF: {err}")
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur PDF : {err}"))
            page.snack_bar.open = True
            page.update()

    boite_resultat = ft.Container(
        content=ft.Column([affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
        width=600,
        height=400,
        bgcolor="#FFFFFF",
        border_radius=10,
        padding=16,
        border=ft.border.all(1, "#BBDEFB"),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Reporting & Qualité des AAV", size=28, weight="bold", color=COLOR_PRIMARY),
                ft.Divider(height=20, color="transparent"),
                champ_chiffre,
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=lambda e: donne_get_metric(), bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Voir Liste Globale", icon=ft.Icons.LIST, on_click=ouvrir_popup_toutes_metrics, bgcolor="#2196F3", color=ft.Colors.WHITE),
                    ft.ElevatedButton("Historique", icon=ft.Icons.HISTORY, on_click=ouvrir_popup_historique, bgcolor=ft.Colors.AMBER_600, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Recalculer", icon=ft.Icons.CALCULATE, on_click=lancer_calcul, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Télécharger PDF", icon=ft.Icons.PICTURE_AS_PDF, on_click=telecharger_pdf, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                ft.Divider(height=15, color="transparent"),
                boite_resultat,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        bgcolor="#FFFFFF",
        expand=True,
        padding=20,
    )


def main(page: ft.Page):
    page.title = "Reporting Métriques & Qualité"
    page.padding = 0
    page.bgcolor = "#F5F5F5"
    page.add(create_metrics_view(page))


if __name__ == "__main__":
    ft.app(target=main)
