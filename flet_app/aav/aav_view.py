import flet as ft
from app.routers import aavs
from app.database import SessionLocal

def create_aav_view(page: ft.Page):
    
    champ_chiffre = ft.TextField(
        label="Numéro AAV", 
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        border_color=ft.Colors.BLUE_400,
        bgcolor=ft.Colors.BLUE_50,
        prefix_icon=ft.Icons.SEARCH,
        cursor_color=ft.Colors.BLUE_700,
    )
    affichage_resultat = ft.Text("Résultat : aucun", size=18, color=ft.Colors.BLUE_700)
    bouton_modifier = ft.ElevatedButton(
        "Modifier", 
        visible=False,
        on_click=lambda e: ouvrir_popup_modifier(e)
    )
    bouton_supprimer = ft.ElevatedButton(
        "Supprimer", 
        visible=False,
        on_click=lambda e: action_supprimer(e),
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.RED
    )
    boite_fixe = ft.Container(
        content=affichage_resultat,
        width=600,
        height=300, 
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
            affichage_resultat.color = ft.Colors.BLACK87
            bouton_modifier.visible = True
            bouton_supprimer.visible = True

            
        except Exception as e:
            affichage_resultat.value = "Aucun AAV ne correspond à ce numéro"
            affichage_resultat.color = ft.Colors.RED
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
            
            # On met à jour l'affichage
            affichage_resultat.value = "AAV supprimé avec succès."
            affichage_resultat.color = ft.Colors.GREEN
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            page.update()
        except Exception as error:
            print("ERREUR SUPPRESSION :", error)


    return ft.Column(
        controls=[
            ft.Text("Information AAV", size=28, weight="bold", color=ft.Colors.BLUE_700),
            champ_chiffre,
            ft.ElevatedButton("Get AAV", on_click=donnee_aav),
            boite_fixe,
            ft.Row([bouton_modifier, bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
