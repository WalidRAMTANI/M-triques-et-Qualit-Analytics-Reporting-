"""
Gestion des Apprenants page – style moderne.
CRUD apprenants, prérequis externes, statuts d'apprentissage, ontologie, progression.
"""

import sys
from pathlib import Path
import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.routers import learners
from app.database import SessionLocal


class LearnersPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_modifier = None
        self.bouton_supprimer = None

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def _fmt(self, res: dict) -> str:
        return "\n".join(f"{k:30}: {v}" for k, v in res.items())

    def rechercher(self, e=None):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = learners.get_learner(int(self.champ_id.value), db)
            self._set_result(self._fmt(res))
            self.bouton_modifier.visible = True
            self.bouton_supprimer.visible = True
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
            self.bouton_modifier.visible = False
            self.bouton_supprimer.visible = False
        finally:
            db.close()
            self._page.update()

    def ouvrir_liste(self, e):
        db = SessionLocal()
        try:
            data = learners.list_learners(db=db)
        except Exception as err:
            self._set_result(f"Erreur liste : {err}", "#F44336")
            db.close()
            return
        db.close()
        items_raw = data if isinstance(data, list) else data.get("learners", [])

        def selectionner(id_v):
            self.champ_id.value = str(id_v)
            dialog.open = False
            self._page.update()
            self.rechercher()

        items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON, color="#1565C0"),
                title=ft.Text(f"Apprenant #{l.get('id_apprenant', l.get('id', '?'))}", weight="bold"),
                subtitle=ft.Text(f"{l.get('nom', '')} {l.get('prenom', '')}"),
                on_click=lambda e, id_v=l.get("id_apprenant", l.get("id")): selectionner(id_v),
            )
            for l in items_raw
        ]
        dialog = ft.AlertDialog(
            title=ft.Text("Liste des Apprenants"),
            content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_creation(self, e):
        champ_nom = ft.TextField(label="Nom", width=300)
        champ_prenom = ft.TextField(label="Prénom", width=300)
        champ_email = ft.TextField(label="Email", width=300)

        def valider(ev):
            db = SessionLocal()
            try:
                res = learners.create_learner({"nom": champ_nom.value, "prenom": champ_prenom.value, "email": champ_email.value}, db)
                dialog.open = False
                id_key = "id_apprenant" if "id_apprenant" in res else "id"
                self.champ_id.value = str(res.get(id_key, ""))
                self._page.update()
                self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur création : {err}", "#F44336")
            finally:
                db.close()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer un Apprenant"),
            content=ft.Column([champ_nom, champ_prenom, champ_email], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Créer", on_click=valider, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_modifier(self, e):
        if not self.champ_id.value:
            return
        champ_nom = ft.TextField(label="Nom", width=300)
        champ_prenom = ft.TextField(label="Prénom", width=300)
        champ_email = ft.TextField(label="Email", width=300)

        def sauvegarder(ev):
            db = SessionLocal()
            try:
                learners.update_learner_full(int(self.champ_id.value), {"nom": champ_nom.value, "prenom": champ_prenom.value, "email": champ_email.value}, db)
                self._set_result("✅ Apprenant modifié avec succès", "#4CAF50")
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                db.close()
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier Apprenant n°{self.champ_id.value}", weight="bold"),
            content=ft.Column([champ_nom, champ_prenom, champ_email], scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Sauvegarder", on_click=sauvegarder, color="#FFFFFF", bgcolor="#4CAF50"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def action_supprimer(self, e):
        if not self.champ_id.value:
            return

        def confirmer(ev):
            db = SessionLocal()
            try:
                learners.delete_learner(int(self.champ_id.value), db)
                self._set_result("✅ Apprenant supprimé", "#4CAF50")
                self.bouton_modifier.visible = False
                self.bouton_supprimer.visible = False
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                db.close()
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression", weight="bold"),
            content=ft.Text(f"Supprimer Apprenant #{self.champ_id.value} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="#FFFFFF", bgcolor="#F44336"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def voir_progression(self, e):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = learners.get_progress(int(self.champ_id.value), db)
            import json
            self._set_result(json.dumps(res, indent=2, ensure_ascii=False))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
        finally:
            db.close()

    def voir_statuts(self, e):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = learners.get_learning_status(int(self.champ_id.value), db)
            import json
            self._set_result(json.dumps(res, indent=2, ensure_ascii=False))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
        finally:
            db.close()

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#1A237E"
        COLOR_BG_INPUT = "#E8EAF6"
        COLOR_BORDER = "#3F51B5"

        self.champ_id = ft.TextField(
            label="Numéro Apprenant",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.PERSON_SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton("Modifier", visible=False, on_click=self.ouvrir_modifier, color="#FFFFFF", bgcolor="#3F51B5")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="#FFFFFF", bgcolor="#F44336")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#C5CAE9"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Gestion des Apprenants", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Liste Apprenants", icon=ft.Icons.GROUP, on_click=self.ouvrir_liste, bgcolor="#3F51B5", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Nouvel Apprenant", icon=ft.Icons.PERSON_ADD, on_click=self.ouvrir_creation, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Row([
                        ft.ElevatedButton("Voir Progression", icon=ft.Icons.TRENDING_UP, on_click=self.voir_progression, bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Statuts d'apprentissage", icon=ft.Icons.BOOKMARK, on_click=self.voir_statuts, bgcolor="#0288D1", color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([self.bouton_modifier, self.bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
