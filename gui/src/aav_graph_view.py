import sys
from pathlib import Path

# Add project root (projet_python) to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../projet_python
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft
import requests
from requests.exceptions import RequestException

def build_aav_graph_view(page: ft.Page, initial_id=None):
    """
    Vue détaillée et recherchable des AAVs (Version Graph).
    """
    # Champ de recherche persistant
    champ_chiffre = ft.TextField(
        label="Numéro AAV (ex: 1)", 
        width=200,
        value=str(initial_id) if initial_id else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        border_color="#2196F3",
        bgcolor="#E3F2FD",
        prefix_icon=ft.Icons.SEARCH,
        cursor_color="#1565C0",
        on_submit=lambda e: donnee_aav(None)
    )
    
    affichage_resultat = ft.Text("Entrez un ID ou utilisez la liste pour charger un AAV", size=16, color="#1565C0")
    
    # Les boutons d'actions ont été retirés à la demande de l'utilisateur
    
    boite_fixe = ft.Container(
        content=ft.Column([affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
        width=600,
        height=350,
        bgcolor="#FFFFFF",
        border_radius=10,
        padding=16,
        border=ft.border.all(1, "#BBDEFB")
    )

    def donnee_aav(e):
        if not champ_chiffre.value:
            return
            
        try:
            response = requests.get(f"http://127.0.0.1:8000/aavs/{int(champ_chiffre.value)}")
            if response.status_code == 200:
                res = response.json()
                affichage_resultat.value = (
                    f"AAV: #{res.get('id_aav')}\n"
                    f"Nom: {res.get('nom')}\n"
                    f"Libelle: {res.get('libelle_integration')}\n"
                    f"Discipline: {res.get('discipline')}\n"
                    f"Enseignement: {res.get('enseignement')}\n\n"
                    f"Description:\n{res.get('description_markdown')}\n"
                )
                affichage_resultat.color = "#212121"
                bouton_modifier.visible = True
                bouton_supprimer.visible = True
            else:
                affichage_resultat.value = f"Erreur: AAV non trouvé pour l'ID {champ_chiffre.value}"
                affichage_resultat.color = "#F44336"
                bouton_modifier.visible = False
                bouton_supprimer.visible = False
        except Exception as err:
            affichage_resultat.value = f"Erreur de connexion au backend"
            affichage_resultat.color = "#F44336"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            
        if page: 
            page.update()

    def ouvrir_liste(e):
        try:
            response = requests.get("http://127.0.0.1:8000/aavs/")
            if response.status_code != 200:
                print("Erreur lors de la récupération de la liste des AAVs")
                return
            tous = response.json()
            
            def charger_id(idx):
                champ_chiffre.value = str(idx)
                dialog.open = False
                page.update()
                donnee_aav(None)

            items = []
            for a in tous:
                items.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.SCHOOL, color="#2196F3"),
                        title=ft.Text(f"AAV #{a.get('id_aav')} - {a.get('nom')}"),
                        subtitle=ft.Text(f"{a.get('discipline')}"),
                        on_click=lambda e, idx=a.get('id_aav'): charger_id(idx)
                    )
                )

            dialog = ft.AlertDialog(
                title=ft.Text("Choisir un AAV"),
                content=ft.Container(ft.ListView(items, spacing=5), height=450, width=400),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or page.update())]
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        except Exception as err:
            print(f"Erreur de connexion: {err}")

    def ouvrir_popup_modifier(e):
        try:
            id_actuel = int(champ_chiffre.value)
            response = requests.get(f"http://127.0.0.1:8000/aavs/{id_actuel}")
            if response.status_code != 200:
                print("Erreur de récupération pour modification")
                return
                
            res = response.json()
            
            champ_nom = ft.TextField(label="Nom", value=res.get("nom", ""))
            champ_desc = ft.TextField(label="Description", value=res.get("description_markdown", ""), multiline=True)

            def sauvegarder(ev):
                try:
                    nouvelles_donnees = {"nom": champ_nom.value, "description_markdown": champ_desc.value}
                    update_response = requests.put(f"http://127.0.0.1:8000/aavs/{id_actuel}", json=nouvelles_donnees)
                    if update_response.status_code == 200:
                        dialog.open = False
                        donnee_aav(None)
                    else:
                        print(f"Erreur lors de la modification: {update_response.text}")
                except Exception as err:
                    print(f"Erreur de connexion: {err}")

            dialog = ft.AlertDialog(
                title=ft.Text(f"Modifier AAV #{id_actuel}"),
                content=ft.Column([champ_nom, champ_desc], tight=True),
                actions=[ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or page.update()), 
                         ft.ElevatedButton("Enregistrer", on_click=sauvegarder)]
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        except Exception as err:
            print(f"Erreur: {err}")

    def action_supprimer(e):
        try:
            response = requests.delete(f"http://127.0.0.1:8000/aavs/{int(champ_chiffre.value)}")
            if response.status_code in [200, 204]:
                affichage_resultat.value = "Supprimé avec succès."
                bouton_modifier.visible = False
                bouton_supprimer.visible = False
                page.update()
            else:
                affichage_resultat.value = f"Erreur lors de la suppression."
                page.update()
        except Exception as err:
            affichage_resultat.value = f"Erreur de connexion au backend"
            page.update()

    # On s'assure que le champ est vide au démarrage pour éviter d'imposer l'ID 1
    champ_chiffre.value = str(initial_id) if initial_id else ""
    
    # Si un ID initial est fourni, on charge les données
    if initial_id:
        donnee_aav(None)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Détails & Recherche AAV", size=28, weight="bold", color="#1565C0"),
                ft.Divider(height=20, color="transparent"),
                ft.Row([
                    champ_chiffre,
                    ft.ElevatedButton("Chercher", icon=ft.Icons.SEARCH, on_click=donnee_aav),
                    ft.ElevatedButton("Liste des AAVs", icon=ft.Icons.LIST, on_click=ouvrir_liste, bgcolor="#1565C0", color="white"),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=15, color="transparent"),
                boite_fixe,
                ft.Divider(height=15, color="transparent"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        padding=20,
    )

def main(page: ft.Page):
    page.add(build_aav_graph_view(page))

if __name__ == "__main__":
    ft.app(target=main)
