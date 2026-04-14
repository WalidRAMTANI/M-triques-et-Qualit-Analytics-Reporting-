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
        content=ft.Column([affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
        width=600,
        height=400,
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
                f"ID Enseignant: {res['id_enseignant']}\n"
                f"Type AAV: {res['type_aav']}\n"
                f"Type Evaluation: {res['type_evaluation']}\n"
                f"Prerequis IDs: {res['prerequis_ids']}\n"
                f"Prerequis Externes: {res['prerequis_externes_codes']}\n"
                f"Code Inter-disc: {res['code_prerequis_interdisciplinaire']}\n"
                f"Ponderation: {res['aav_enfant_ponderation']}\n"
                f"IDs Exercices: {res['ids_exercices']}\n"
                f"Prompts IDs: {res['prompts_fabrication_ids']}\n"
                f"Regles Progression: {res['regles_progression']}\n"
                f"Est Actif: {res['is_active']}\n"
                f"Version: {res['version']}\n"
                f"Créé le: {res['created_at']}\n"
                f"Mis à jour le: {res['updated_at']}\n"
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
            champ_desc = ft.TextField(label="Description", value=res["description_markdown"], multiline=True)
            champ_type_aav = ft.TextField(label="Type AAV", value=res["type_aav"])
            champ_evaluation = ft.TextField(label="Type Evaluation", value=res["type_evaluation"])
            champ_is_active = ft.Checkbox(label="Est Actif", value=res["is_active"])
            champ_prerequis = ft.TextField(label="Prerequis IDs (JSON)", value=str(res["prerequis_ids"]))
            champ_enseignant = ft.TextField(label="ID Enseignant", value=str(res["id_enseignant"]))

            def sauvegarder(ev):
                db2 = SessionLocal()
                nouvelles_donnees = {
                    "nom": champ_nom.value,
                    "libelle_integration": champ_libelle.value,
                    "discipline": champ_discipline.value,
                    "enseignement": champ_enseignement.value,
                    "description_markdown": champ_desc.value,
                    "type_aav": champ_type_aav.value,
                    "type_evaluation": champ_evaluation.value,
                    "is_active": champ_is_active.value,
                    "id_enseignant": int(champ_enseignant.value) if champ_enseignant.value.isdigit() else None
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
                content=ft.Container(
                    content=ft.Column([
                        champ_nom, 
                        champ_libelle, 
                        champ_discipline, 
                        champ_enseignement, 
                        champ_desc,
                        champ_type_aav,
                        champ_evaluation,
                        champ_is_active,
                        champ_prerequis,
                        champ_enseignant
                    ], scroll=ft.ScrollMode.ALWAYS),
                    width=400,
                    height=500,
                ),
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

    def ouvrir_popup_creation(e):
        try:
            champ_nom = ft.TextField(label="Nom")
            champ_libelle = ft.TextField(label="Libellé")
            champ_discipline = ft.TextField(label="Discipline")
            champ_enseignement = ft.TextField(label="Enseignement")
            champ_desc = ft.TextField(label="Description", multiline=True)
            champ_type_aav = ft.TextField(label="Type AAV")
            champ_evaluation = ft.TextField(label="Type Evaluation")
            champ_is_active = ft.Checkbox(label="Est Actif", value=True)
            champ_enseignant = ft.TextField(label="ID Enseignant", value="1")

            def valider_creation(ev):
                db = SessionLocal()
                donnees = {
                    "nom": champ_nom.value,
                    "libelle_integration": champ_libelle.value,
                    "discipline": champ_discipline.value,
                    "enseignement": champ_enseignement.value,
                    "description_markdown": champ_desc.value,
                    "type_aav": champ_type_aav.value,
                    "type_evaluation": champ_evaluation.value,
                    "is_active": champ_is_active.value,
                    "id_enseignant": int(champ_enseignant.value) if champ_enseignant.value.isdigit() else None
                }
                res = aavs.create_aav(donnees, db)
                db.close()
                dialog.open = False
                
                # On affiche le résultat de la création
                champ_chiffre.value = str(res["id_aav"])
                page.update()
                donnee_aav(None)

            def annuler(ev):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Créer un nouvel AAV"),
                content=ft.Container(
                    content=ft.Column([
                        champ_nom, champ_libelle, champ_discipline, champ_enseignement, 
                        champ_desc, champ_type_aav, champ_evaluation, champ_is_active, 
                        champ_enseignant
                    ], scroll=ft.ScrollMode.ALWAYS),
                    width=400,
                    height=500,
                ),
                actions=[
                    ft.TextButton("Annuler", on_click=annuler),
                    ft.ElevatedButton("Créer", on_click=valider_creation)
                ]
            )
            
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
            
        except Exception as error:
            print("ERREUR CREATION POPUP :", error)

    def ouvrir_popup_tous_aavs(e):
        try:
            db = SessionLocal()
            liste_aavs = aavs.get_aavs(db=db)
            db.close()

            def charger_aav(id_aav):
                champ_chiffre.value = str(id_aav)
                dialog.open = False
                page.update()
                donnee_aav(None)

            items_list = []
            for item in liste_aavs:
                items_list.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.BLUE_400),
                        title=ft.Text(f"{item['nom']} (ID: {item['id_aav']})", weight="bold"),
                        subtitle=ft.Text(f"Discipline: {item['discipline']} | Type: {item['type_aav']}"),
                        on_click=lambda e, id_v=item['id_aav']: charger_aav(id_v)
                    )
                )

            dialog = ft.AlertDialog(
                title=ft.Text("Liste de tous les AAVs"),
                content=ft.Container(
                    content=ft.ListView(items_list, spacing=10, padding=10),
                    width=500,
                    height=600,
                ),
                actions=[
                    ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or page.update())
                ]
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        except Exception as error:
            print("ERREUR LISTE POPUP :", error)

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
                    ft.Row([
                        ft.ElevatedButton("Get AAV", on_click=donnee_aav, icon=ft.Icons.SEARCH),
                        ft.ElevatedButton("Créer Nouveau AAV", on_click=ouvrir_popup_creation, icon=ft.Icons.ADD, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Voir Liste AAVs", on_click=ouvrir_popup_tous_aavs, icon=ft.Icons.LIST, bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER),
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
    ft.app(target=main)