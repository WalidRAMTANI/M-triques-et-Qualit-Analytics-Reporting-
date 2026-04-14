import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2] 
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft
from app.routers import sessions
from app.database import SessionLocal

def build_session_view(page: ft.Page):
    champ_chiffre = ft.TextField(
        label="Numéro Session", 
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        border_color="#9C27B0",
        bgcolor="#F3E5F5",
        prefix_icon=ft.Icons.SEARCH,
        cursor_color="#7B1FA2",
    )
    
    affichage_resultat = ft.Text("Résultat : aucun", size=18, color="#7B1FA2")
    
    bouton_modifier = ft.ElevatedButton(
        "Modifier d'état", 
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
        border=ft.border.all(1, "#E1BEE7")
    )

    def donnee_session(e):
        if not champ_chiffre.value:
            return
            
        db = SessionLocal()
        try:
            res = sessions.get_session(int(champ_chiffre.value), db)
            affichage_resultat.value = (
                f"Session ID: {res['id_session']}\n"
                f"ID Activité: {res['id_activite']}\n"
                f"ID Apprenant: {res['id_apprenant']}\n"
                f"Statut: {res['statut'].upper()}\n"
                f"Date Début: {res['date_debut']}\n"
                f"Date Fin: {res['date_fin']}\n"
                f"Bilan: {res['bilan']}\n"
            )
            affichage_resultat.color = "#212121"
            bouton_modifier.visible = True
            bouton_supprimer.visible = True
            
        except Exception as e:
            affichage_resultat.value = "Aucune session ne correspond à ce numéro"
            affichage_resultat.color = "#F44336"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            
        finally:
            db.close()
            page.update() 

    def ouvrir_popup_creation(e):
        try:
            champ_activite = ft.TextField(label="ID Activité", keyboard_type=ft.KeyboardType.NUMBER)
            champ_apprenant = ft.TextField(label="ID Apprenant", keyboard_type=ft.KeyboardType.NUMBER)

            def valider_creation(ev):
                if not champ_activite.value or not champ_apprenant.value:
                    return
                
                db = SessionLocal()
                try:
                    donnees = {
                        "id_activite": int(champ_activite.value),
                        "id_apprenant": int(champ_apprenant.value)
                    }
                    res = sessions.create_session(donnees, db)
                    dialog.open = False
                    champ_chiffre.value = str(res["id_session"])
                    page.update()
                    donnee_session(None)
                except Exception as err:
                    print(f"Erreur création: {err}")
                finally:
                    db.close()

            def annuler(ev):
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Créer une nouvelle session"),
                content=ft.Column([champ_activite, champ_apprenant], tight=True),
                actions=[
                    ft.TextButton("Annuler", on_click=annuler),
                    ft.ElevatedButton("Créer", on_click=valider_creation, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE)
                ]
            )
            
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
            
        except Exception as error:
            print("ERREUR CREATION POPUP :", error)

    def ouvrir_popup_modifier(e):
        try:
            db = SessionLocal()
            id_actuel = int(champ_chiffre.value)
            res = sessions.get_session(id_actuel, db)
            db.close() 

            def changer_statut(nouveau_statut):
                db2 = SessionLocal()
                try:
                    if nouveau_statut == "started":
                        sessions.start_session(id_actuel, db2)
                    elif nouveau_statut == "closed":
                        sessions.close_session(id_actuel, db2)
                    
                    dialog.open = False
                    page.update()
                    donnee_session(None)
                except Exception as err:
                    print(f"Erreur modif: {err}")
                finally:
                    db2.close()

            dialog = ft.AlertDialog(
                title=ft.Text(f"Modifier Session n°{id_actuel}"),
                content=ft.Text(f"Statut actuel : {res['statut']}"),
                actions=[
                    ft.ElevatedButton("Démarrer", on_click=lambda _: changer_statut("started"), bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Clôturer", on_click=lambda _: changer_statut("closed"), bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE),
                    ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or page.update())
                ]
            )
            
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
            
        except Exception as error:
            print("ERREUR MODIF POPUP :", error)

    def ouvrir_popup_toutes_sessions(e):
        try:
            db = SessionLocal()
            res = sessions.list_sessions(db=db)
            liste_sessions = res.get("sessions", [])
            db.close()

            def charger_session(id_s):
                champ_chiffre.value = str(id_s)
                dialog.open = False
                page.update()
                donnee_session(None)

            items_list = []
            for s in liste_sessions:
                items_list.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color=ft.Colors.PURPLE_400),
                        title=ft.Text(f"Session {s['id_session']} (Apprenant: {s['id_apprenant']})", weight="bold"),
                        subtitle=ft.Text(f"Activité: {s['id_activite']} | Statut: {s['statut']}"),
                        on_click=lambda e, id_v=s['id_session']: charger_session(id_v)
                    )
                )

            dialog = ft.AlertDialog(
                title=ft.Text("Liste de toutes les Sessions"),
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
            sessions.delete_session(id_actuel, db)
            db.close()
            
            affichage_resultat.value = "Session supprimée avec succès."
            affichage_resultat.color = "#4CAF50"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            page.update()
        except Exception as error:
            print("ERREUR SUPPRESSION :", error)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Gestion des Sessions", size=28, weight="bold", color="#7B1FA2"),
                ft.Divider(height=20, color="transparent"),
                champ_chiffre,
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    ft.ElevatedButton("Rechercher", on_click=donnee_session, icon=ft.Icons.SEARCH),
                    ft.ElevatedButton("Nouvelle Session", on_click=ouvrir_popup_creation, icon=ft.Icons.ADD, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Liste des Sessions", on_click=ouvrir_popup_toutes_sessions, icon=ft.Icons.LIST, bgcolor=ft.Colors.PURPLE_400, color=ft.Colors.WHITE),
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

def main(page: ft.Page):
    page.add(build_session_view(page))

if __name__ == "__main__":
    ft.app(target=main)
