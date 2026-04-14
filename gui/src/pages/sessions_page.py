"""
Sessions page – style moderne (inspiré directement de session.py de référence).
Gestion des sessions : rechercher, créer, démarrer, clôturer, supprimer.
Correspond aux 5 endpoints du router sessions.py.
"""

import sys
from pathlib import Path
import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.routers import sessions
from app.database import SessionLocal


class SessionsPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_demarrer = None
        self.bouton_cloturer = None
        self.bouton_supprimer = None

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    # ── Endpoint GET /{id} ────────────────────────────────────────────────────

    def rechercher(self, e=None):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = sessions.get_session(int(self.champ_id.value), db)
            self._set_result(
                f"Session ID     : {res['id_session']}\n"
                f"ID Activité    : {res['id_activite']}\n"
                f"ID Apprenant   : {res['id_apprenant']}\n"
                f"Statut         : {res['statut'].upper()}\n"
                f"Date Début     : {res['date_debut']}\n"
                f"Date Fin       : {res['date_fin']}\n"
                f"Bilan          : {res['bilan']}\n"
            )
            self.bouton_demarrer.visible = True
            self.bouton_cloturer.visible = True
            self.bouton_supprimer.visible = True
        except Exception as err:
            self._set_result(f"Aucune session ne correspond à ce numéro\n{err}", "#F44336")
            self.bouton_demarrer.visible = False
            self.bouton_cloturer.visible = False
            self.bouton_supprimer.visible = False
        finally:
            db.close()
            self._page.update()

    # ── Endpoint GET / – Liste popup ─────────────────────────────────────────

    def ouvrir_liste(self, e):
        db = SessionLocal()
        try:
            res = sessions.list_sessions(db=db)
            liste = res.get("sessions", [])
        except Exception as err:
            self._set_result(f"Erreur liste : {err}", "#F44336")
            db.close()
            return
        db.close()

        def charger(id_s):
            self.champ_id.value = str(id_s)
            dialog.open = False
            self._page.update()
            self.rechercher()

        items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color="#7B1FA2"),
                title=ft.Text(f"Session {s['id_session']} (Apprenant: {s['id_apprenant']})", weight="bold"),
                subtitle=ft.Text(f"Activité: {s['id_activite']} | Statut: {s['statut']}"),
                on_click=lambda e, id_v=s["id_session"]: charger(id_v),
            )
            for s in liste
        ]
        dialog = ft.AlertDialog(
            title=ft.Text("Liste de toutes les Sessions"),
            content=ft.Container(content=ft.ListView(items, spacing=10, padding=10), width=500, height=500),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    # ── Endpoint POST / – Créer ───────────────────────────────────────────────

    def ouvrir_creation(self, e):
        champ_activite = ft.TextField(label="ID Activité", keyboard_type=ft.KeyboardType.NUMBER)
        champ_apprenant = ft.TextField(label="ID Apprenant", keyboard_type=ft.KeyboardType.NUMBER)

        def valider(ev):
            if not champ_activite.value or not champ_apprenant.value:
                return
            db = SessionLocal()
            try:
                donnees = {
                    "id_activite": int(champ_activite.value),
                    "id_apprenant": int(champ_apprenant.value),
                }
                res = sessions.create_session(donnees, db)
                dialog.open = False
                self.champ_id.value = str(res["id_session"])
                self._page.update()
                self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur création : {err}", "#F44336")
            finally:
                db.close()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer une nouvelle Session"),
            content=ft.Column([champ_activite, champ_apprenant], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Créer", on_click=valider, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    # ── Endpoint PUT /{id}/start ──────────────────────────────────────────────

    def demarrer(self, e):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            sessions.start_session(int(self.champ_id.value), db)
            self._set_result("✅ Session démarrée avec succès.", "#4CAF50")
            self.rechercher()
        except Exception as err:
            self._set_result(f"❌ Erreur démarrage : {err}", "#F44336")
        finally:
            db.close()

    # ── Endpoint PUT /{id}/close ──────────────────────────────────────────────

    def cloturer(self, e):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = sessions.close_session(int(self.champ_id.value), db)
            bilan = res.get("summary", {})
            self._set_result(
                f"✅ Session clôturée\n"
                f"{'─' * 40}\n"
                f"Total tentatives : {bilan.get('total_attempts', 'N/A')}\n"
                f"Tentatives valides : {bilan.get('valid_attempts', 'N/A')}\n"
                f"Score moyen : {bilan.get('average_score', 0):.2f}\n",
                "#4CAF50",
            )
        except Exception as err:
            self._set_result(f"❌ Erreur clôture : {err}", "#F44336")
        finally:
            db.close()

    # ── Endpoint DELETE /{id} ─────────────────────────────────────────────────

    def action_supprimer(self, e):
        if not self.champ_id.value:
            return

        def confirmer(ev):
            db = SessionLocal()
            try:
                sessions.delete_session(int(self.champ_id.value), db)
                self._set_result("✅ Session supprimée avec succès.", "#4CAF50")
                self.bouton_demarrer.visible = False
                self.bouton_cloturer.visible = False
                self.bouton_supprimer.visible = False
            except Exception as err:
                self._set_result(f"❌ Erreur suppression : {err}", "#F44336")
            finally:
                db.close()
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression", weight="bold"),
            content=ft.Text(f"Supprimer la Session #{self.champ_id.value} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="#FFFFFF", bgcolor="#F44336"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#7B1FA2"
        COLOR_BG_INPUT = "#F3E5F5"
        COLOR_BORDER = "#9C27B0"

        self.champ_id = ft.TextField(
            label="Numéro Session",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_demarrer = ft.ElevatedButton(
            "Démarrer", visible=False, on_click=self.demarrer,
            color="#FFFFFF", bgcolor=ft.Colors.BLUE_400,
        )
        self.bouton_cloturer = ft.ElevatedButton(
            "Clôturer", visible=False, on_click=self.cloturer,
            color="#FFFFFF", bgcolor=ft.Colors.AMBER_700,
        )
        self.bouton_supprimer = ft.ElevatedButton(
            "Supprimer", visible=False, on_click=self.action_supprimer,
            color="#FFFFFF", bgcolor="#F44336",
        )

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#E1BEE7"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Gestion des Sessions", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Nouvelle Session", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Liste des Sessions", icon=ft.Icons.LIST, on_click=self.ouvrir_liste, bgcolor=ft.Colors.PURPLE_400, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([self.bouton_demarrer, self.bouton_cloturer, self.bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
