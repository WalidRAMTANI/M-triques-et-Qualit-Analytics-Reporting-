"""
Ontologies page – style moderne.
CRUD sur les ontologies de référence.
"""

import sys
from pathlib import Path
import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.routers import ontologies
from app.database import SessionLocal


class OntologiesPage:
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
        lines = []
        for k, v in res.items():
            lines.append(f"{k:25}: {v}")
        return "\n".join(lines)

    def rechercher(self, e=None):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = ontologies.get_single_ontology(int(self.champ_id.value), db)
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
            res_list = ontologies.get_ontologies(db=db)
        except Exception as err:
            self._set_result(f"Erreur liste : {err}", "#F44336")
            db.close()
            return
        db.close()

        def selectionner(id_v):
            self.champ_id.value = str(id_v)
            dialog.open = False
            self._page.update()
            self.rechercher()

        items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.ACCOUNT_TREE, color="#4A148C"),
                title=ft.Text(f"Ontologie #{o.get('id_reference', o.get('id', '?'))} — {o.get('nom', '')}", weight="bold"),
                subtitle=ft.Text(str(o.get("description", ""))[:80]),
                on_click=lambda e, id_v=o.get("id_reference", o.get("id")): selectionner(id_v),
            )
            for o in res_list
        ]
        dialog = ft.AlertDialog(
            title=ft.Text("Liste des Ontologies"),
            content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_creation(self, e):
        champ_nom = ft.TextField(label="Nom", width=420)
        champ_desc = ft.TextField(label="Description", width=420, min_lines=3, max_lines=5)

        def valider(ev):
            db = SessionLocal()
            try:
                res = ontologies.create_ontology({"nom": champ_nom.value, "description": champ_desc.value}, db)
                dialog.open = False
                self.champ_id.value = str(res.get("id_reference", res.get("id", "")))
                self._page.update()
                self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur création : {err}", "#F44336")
            finally:
                db.close()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer une Ontologie"),
            content=ft.Column([champ_nom, champ_desc], tight=True),
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
        champ_nom = ft.TextField(label="Nom", width=420)
        champ_desc = ft.TextField(label="Description", width=420, min_lines=3, max_lines=5)

        def sauvegarder(ev):
            db = SessionLocal()
            try:
                ontologies.update_ontology(int(self.champ_id.value), {"nom": champ_nom.value, "description": champ_desc.value}, db)
                self._set_result("✅ Ontologie modifiée avec succès", "#4CAF50")
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                db.close()
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier Ontologie n°{self.champ_id.value}", weight="bold"),
            content=ft.Column([champ_nom, champ_desc], scroll=ft.ScrollMode.AUTO),
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
                ontologies.delete_ontology(int(self.champ_id.value), db)
                self._set_result("✅ Ontologie supprimée", "#4CAF50")
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
            content=ft.Text(f"Supprimer Ontologie #{self.champ_id.value} ?"),
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
        COLOR_PRIMARY = "#4A148C"
        COLOR_BG_INPUT = "#EDE7F6"
        COLOR_BORDER = "#7B1FA2"

        self.champ_id = ft.TextField(
            label="Numéro Ontologie",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton("Modifier", visible=False, on_click=self.ouvrir_modifier, color="#FFFFFF", bgcolor="#7B1FA2")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="#FFFFFF", bgcolor="#F44336")

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
                    ft.Text("Ontologies de Référence", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Voir toutes", icon=ft.Icons.LIST, on_click=self.ouvrir_liste, bgcolor="#7B1FA2", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Nouvelle", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([self.bouton_modifier, self.bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
