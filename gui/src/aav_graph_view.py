import sys
from pathlib import Path

# Add project root (projet_python) to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../projet_python
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft
from app.routers import aavs
from app.database import SessionLocal

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
    
    # Boutons d'actions
    bouton_modifier = ft.ElevatedButton(
        "Modifier", 
        visible=False,
        on_click=lambda e: ouvrir_popup_modifier(e)
    )
    bouton_supprimer = ft.ElevatedButton(
        "Supprimer", 
        visible=False,
        on_click=lambda e: action_supprimer(e),
        color="#FFFFFF",
        bgcolor="#F44336"
    )
    
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
            
        db = SessionLocal()
        try:
            res = aavs.get_aav(int(champ_chiffre.value), db)
            affichage_resultat.value = (
                f"AAV: #{res['id_aav']}\n"
                f"Nom: {res['nom']}\n"
                f"Libelle: {res['libelle_integration']}\n"
                f"Discipline: {res['discipline']}\n"
                f"Enseignement: {res['enseignement']}\n\n"
                f"Description:\n{res['description_markdown']}\n"
            )
            affichage_resultat.color = "#212121"
            bouton_modifier.visible = True
            bouton_supprimer.visible = True
            
        except Exception:
            affichage_resultat.value = f"Aucun AAV trouvé pour l'ID {champ_chiffre.value}"
            affichage_resultat.color = "#F44336"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            
        finally:
            db.close()
            if page: page.update() 

    def ouvrir_liste(e):
        db = SessionLocal()
        try:
            tous = aavs.list_aavs(db)
            
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
                        title=ft.Text(f"AAV #{a['id_aav']} - {a['nom']}"),
                        subtitle=ft.Text(f"{a['discipline']}"),
                        on_click=lambda e, idx=a['id_aav']: charger_id(idx)
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
        finally:
            db.close()

    def ouvrir_popup_modifier(e):
        db = SessionLocal()
        try:
            id_actuel = int(champ_chiffre.value)
            res = aavs.get_aav(id_actuel, db)
            
            champ_nom = ft.TextField(label="Nom", value=res["nom"])
            champ_desc = ft.TextField(label="Description", value=res["description_markdown"], multiline=True)

            def sauvegarder(ev):
                db2 = SessionLocal()
                try:
                    nouvelles_donnees = {"nom": champ_nom.value, "description_markdown": champ_desc.value}
                    aavs.update_aav(id_actuel, nouvelles_donnees, db2)
                    dialog.open = False
                    donnee_aav(None)
                finally:
                    db2.close()

            dialog = ft.AlertDialog(
                title=ft.Text(f"Modifier AAV #{id_actuel}"),
                content=ft.Column([champ_nom, champ_desc], tight=True),
                actions=[ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or page.update()), 
                         ft.ElevatedButton("Enregistrer", on_click=sauvegarder)]
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
        finally:
            db.close()

    def action_supprimer(e):
        db = SessionLocal()
        try:
            aavs.delete_aav(int(champ_chiffre.value), db)
            affichage_resultat.value = "Supprimé avec succès."
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            page.update()
        finally:
            db.close()

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
                ft.Row([bouton_modifier, bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER),
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
