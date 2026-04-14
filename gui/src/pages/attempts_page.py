"""
Attempts (Tentatives) page – style moderne.
Recherche, création, suppression et traitement des tentatives d'exercices.
"""

import sys
from pathlib import Path
import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.routers import attempts as att
from app.database import SessionLocal


class AttemptsPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_supprimer = None
        self.bouton_traiter = None

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def _fmt(self, res: dict) -> str:
        lines = [f"{k:25}: {v}" for k, v in res.items()]
        return "\n".join(lines)

    def rechercher(self, e=None):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = att.get_attempt(int(self.champ_id.value), db)
            self._set_result(self._fmt(res))
            self.bouton_supprimer.visible = True
            self.bouton_traiter.visible = True
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
            self.bouton_supprimer.visible = False
            self.bouton_traiter.visible = False
        finally:
            db.close()
            self._page.update()

    def ouvrir_liste(self, e):
        db = SessionLocal()
        try:
            res_list = att.list_attempts(db=db)
        except Exception as err:
            self._set_result(f"Erreur liste : {err}", "#F44336")
            db.close()
            return
        db.close()

        items_raw = res_list if isinstance(res_list, list) else res_list.get("attempts", [])

        def selectionner(id_v):
            self.champ_id.value = str(id_v)
            dialog.open = False
            self._page.update()
            self.rechercher()

        items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.ASSIGNMENT, color="#E65100"),
                title=ft.Text(f"Tentative #{t.get('id', t.get('id_tentative', '?'))}", weight="bold"),
                subtitle=ft.Text(f"Score: {t.get('score_obtenu', 'N/A')} | Valide: {t.get('est_valide', 'N/A')}"),
                on_click=lambda e, id_v=t.get("id", t.get("id_tentative")): selectionner(id_v),
            )
            for t in items_raw
        ]
        dialog = ft.AlertDialog(
            title=ft.Text("Liste des Tentatives"),
            content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_creation(self, e):
        champ_apprenant = ft.TextField(label="ID Apprenant", keyboard_type=ft.KeyboardType.NUMBER, width=250)
        champ_activite = ft.TextField(label="ID Activité", keyboard_type=ft.KeyboardType.NUMBER, width=250)
        champ_exercice = ft.TextField(label="ID Exercice", keyboard_type=ft.KeyboardType.NUMBER, width=250)

        def valider(ev):
            db = SessionLocal()
            try:
                donnees = {
                    "id_apprenant": int(champ_apprenant.value) if champ_apprenant.value else None,
                    "id_activite": int(champ_activite.value) if champ_activite.value else None,
                    "id_exercice": int(champ_exercice.value) if champ_exercice.value else None,
                }
                res = att.create_attempt(donnees, db)
                dialog.open = False
                id_key = "id" if "id" in res else "id_tentative"
                self.champ_id.value = str(res.get(id_key, ""))
                self._page.update()
                self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur création : {err}", "#F44336")
            finally:
                db.close()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer une Tentative"),
            content=ft.Column([champ_apprenant, champ_activite, champ_exercice], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Créer", on_click=valider, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def traiter(self, e):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = att.process_attempt(int(self.champ_id.value), db)
            self._set_result(f"✅ Tentative traitée\n{self._fmt(res) if isinstance(res, dict) else str(res)}", "#4CAF50")
        except Exception as err:
            self._set_result(f"❌ Erreur traitement : {err}", "#F44336")
        finally:
            db.close()
            self._page.update()

    def action_supprimer(self, e):
        if not self.champ_id.value:
            return

        def confirmer(ev):
            db = SessionLocal()
            try:
                att.delete_attempt(int(self.champ_id.value), db)
                self._set_result("✅ Tentative supprimée", "#4CAF50")
                self.bouton_supprimer.visible = False
                self.bouton_traiter.visible = False
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                db.close()
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression", weight="bold"),
            content=ft.Text(f"Supprimer la tentative #{self.champ_id.value} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="#FFFFFF", bgcolor="#F44336"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#E65100"
        COLOR_BG_INPUT = "#FBE9E7"
        COLOR_BORDER = "#FF5722"

        self.champ_id = ft.TextField(
            label="Numéro Tentative",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="#FFFFFF", bgcolor="#F44336")
        self.bouton_traiter = ft.ElevatedButton("Traiter", visible=False, on_click=self.traiter, color="#FFFFFF", bgcolor="#FF9800")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#FFCCBC"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Tentatives d'Exercices", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Liste des Tentatives", icon=ft.Icons.LIST, on_click=self.ouvrir_liste, bgcolor="#FF5722", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Nouvelle Tentative", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([self.bouton_traiter, self.bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
