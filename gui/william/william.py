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

def main(page: ft.Page):
    page.padding = 0
    page.bgcolor = "#F5F5F5"
    champ_chiffre = ft.TextField(
        label="Numéro AAV", 
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        border_color="#2196F3",
        bgcolor="#E3F2FD",
        prefix_icon=ft.Icons.SEARCH,
        cursor_color="#1565C0",
    )
    affichage_resultat = ft.Text("Résultat : aucun", size=18, color="#1565C0")
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
        content=affichage_resultat,
        width=600,
        height=300,
        bgcolor="#FFFFFF",
        border_radius=10,
        padding=16,
    )

    def donnee_aav(e):
        if not champ_chiffre.value:
            return
            
        db = SessionLocal()
        try:
            res = aavs.get_aav(int(champ_chiffre.value), db)
            affichage_resultat.value = (
                f"AAV: {res['id_aav']}\n"
                f"Nom: {res['nom']}\n"
                f"Libelle Integration: {res['libelle_integration']}\n"
                f"Discipline: {res['discipline']}\n"
                f"Enseignement: {res['enseignement']}\n"
                f"Description: {res['description_markdown']}\n"
            )
            affichage_resultat.color = "#212121"
            bouton_modifier.visible = True
            bouton_supprimer.visible = True

            
        except Exception as e:
            affichage_resultat.value = "Aucun AAV ne correspond à ce numéro"
            affichage_resultat.color = "#F44336"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            
        finally:
            page.update() 

    def ouvrir_popup_modifier(e):
        try:
            print("Lancement de la pop-up...")
            db = SessionLocal()
            id_actuel = int(champ_chiffre.value)
            res = aavs.get_aav(id_actuel, db)
            db.close() 
            
            champ_nom = ft.TextField(label="Nom", value=res["nom"])
            champ_libelle = ft.TextField(label="Libellé", value=res["libelle_integration"])
            champ_discipline = ft.TextField(label="Discipline", value=res["discipline"])
            champ_enseignement = ft.TextField(label="Enseignement", value=res["enseignement"])
            champ_desc = ft.TextField(label="Description", value=res["description_markdown"])

            def sauvegarder(ev):
                db2 = SessionLocal()
                nouvelles_donnees = {
                    "nom": champ_nom.value,
                    "libelle_integration": champ_libelle.value,
                    "discipline": champ_discipline.value,
                    "enseignement": champ_enseignement.value,
                    "description_markdown": champ_desc.value
                }
                aavs.update_aav(id_actuel, nouvelles_donnees, db2)
                db2.close()
                dialog.open = False
                page.update()
                donnee_aav(None) 
                
            def annuler(ev):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                title=ft.Text(f"Modifier AAV n°{id_actuel}"),
                content=ft.Column([champ_nom, champ_libelle, champ_discipline, champ_enseignement, champ_desc]), 
                actions=[
                    ft.TextButton("Annuler", on_click=annuler),
                    ft.ElevatedButton("Sauvegarder", on_click=sauvegarder)
                ]
            )
            
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
            print("Pop-up affichée avec succès !")
            
        except Exception as error:
            print("ERREUR FATALE POPUP :", error)

    def action_supprimer(e):
        try:
            db = SessionLocal()
            id_actuel = int(champ_chiffre.value)
            aavs.delete_aav(id_actuel, db)
            db.close()
            
            affichage_resultat.value = "AAV supprimé avec succès."
            affichage_resultat.color = "#4CAF50"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            page.update()
        except Exception as error:
            print("ERREUR SUPPRESSION :", error)

    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Information AAV", size=28, weight="bold", color="#1565C0"),
                    ft.Divider(height=20, color="transparent"),
                    champ_chiffre,
                    ft.Divider(height=10, color="transparent"),
                    ft.ElevatedButton("Get AAV", on_click=donnee_aav),
                    ft.Divider(height=15, color="transparent"),
                    boite_fixe,
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([bouton_modifier, bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)