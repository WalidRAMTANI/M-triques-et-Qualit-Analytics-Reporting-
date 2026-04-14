import sys
import os
import base64
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2] 
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft
from app.routers import metrics, reports
from app.model.schemas import RapportRequest

def create_metrics_view(page: ft.Page):
    # Thème William (Bleu)
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
        
        try:
            res = metrics.metrique_qualite_aav(target_id)
            affichage_resultat.value = (
                f"METRIQUES POUR L'AAV #{res['id_aav']}\n"
                f"{'─' * 40}\n"
                f"Couverture ressources : {res['score_covering_ressources']*100:.1f}%\n"
                f"Taux de succès moyen : {res['taux_succes_moyen']*100:.1f}%\n"
                f"Est utilisable : {'OUI' if res['est_utilisable'] else 'NON'}\n"
                f"Tentatives totales : {res['nb_tentatives_total']}\n"
                f"Apprenants distincts : {res['nb_apprenants_distincts']}\n"
                f"Ecart-type scores : {res['ecart_type_scores']:.3f}\n"
                f"Date de calcul : {res['date_calcul']}\n"
            )
            affichage_resultat.color = COLOR_TEXT_RESULT
            if not id_aav: champ_chiffre.value = str(target_id)
        except Exception as err:
            affichage_resultat.value = f"Erreur : aucune métrique pour l'AAV {target_id}"
            affichage_resultat.color = ft.Colors.RED_700
            print(f"DEBUG Erreur: {err}")
        finally:
            page.update()

    def ouvrir_popup_toutes_metrics(e):
        try:
            res_list = metrics.get_all_metrics_route()
            
            def selectionner_aav(id_v):
                donne_get_metric(id_v)
                dialog.open = False
                page.update()

            items_list = []
            for m in res_list:
                items_list.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ANALYTICS, color=COLOR_PRIMARY),
                        title=ft.Text(f"AAV #{m.id_aav}", weight="bold"),
                        subtitle=ft.Text(f"Succès: {m.taux_succes_moyen*100:.1f}% | Tentatives: {m.nb_tentatives_total}"),
                        on_click=lambda e, id_v=m.id_aav: selectionner_aav(id_v)
                    )
                )

            dialog = ft.AlertDialog(
                title=ft.Text("Liste de toutes les Métriques"),
                content=ft.Container(
                    content=ft.ListView(items_list, spacing=10, padding=10),
                    width=500, height=600
                ),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or page.update())]
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        except Exception as err:
            print(f"ERREUR LISTE POPUP : {err}")
            affichage_resultat.value = f"Erreur Liste: {err}"
            page.update()

    def ouvrir_popup_historique(e):
        if not champ_chiffre.value:
            return
        try:
            id_actuel = int(champ_chiffre.value)
            hist = metrics.get_history_metrics(id_actuel)
            items_list = []
            for h in hist:
                date_str = str(h['date_calcul'])[:16]
                items_list.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.TIMELINE, color=ft.Colors.AMBER_700),
                        title=ft.Text(f"Calcul du {date_str}"),
                        subtitle=ft.Text(f"Succès: {h['taux_succes_moyen']*100:.1f}% | Util: {'Oui' if h['est_utilisable'] else 'Non'}"),
                    )
                )

            dialog = ft.AlertDialog(
                title=ft.Text(f"Historique AAV #{id_actuel}"),
                content=ft.Container(
                    content=ft.ListView(items_list, spacing=10, padding=10),
                    width=500, height=600
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
            metrics.calculate_metric(int(champ_chiffre.value))
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
            # Appel au routeur de rapports
            request = RapportRequest(type_rapport="aav", id_cible=target_id, format="pdf")
            rapport = reports.generate_rapport_personnalise(request)
            
            # Décoder le base64 contenu dans rapport.contenu
            # Note: to_json a été utilisé dans le service, donc contenu est une string JSON d'un base64
            # On va essayer de décoder directement
            import json
            raw_content = json.loads(rapport.contenu)
            pdf_bytes = base64.b64decode(raw_content)

            # Créer dossier exports
            export_path = Path("exports")
            export_path.mkdir(exist_ok=True)
            
            filename = export_path / f"rapport_aav_{target_id}.pdf"
            with open(filename, "wb") as f:
                f.write(pdf_bytes)
            
            page.snack_bar = ft.SnackBar(ft.Text(f"Rapport enregistré : {filename}"))
            page.snack_bar.open = True
            page.update()
        except Exception as err:
            print(f"Erreur PDF: {err}")
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur lors de la génération PDF : {err}"))
            page.snack_bar.open = True
            page.update()

    # Grand carré blanc comme William
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
                ], alignment=ft.MainAxisAlignment.CENTER),
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
