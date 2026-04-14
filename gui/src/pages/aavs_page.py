"""
AAVs page – style épuré (fond blanc, champ de recherche, boîte résultat,
boutons colorés, popups AlertDialog).
"""

import sys
from pathlib import Path
import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.routers import aavs
from app.database import SessionLocal


class AavsPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_modifier = None
        self.bouton_supprimer = None

    # ─── helpers ──────────────────────────────────────────────────────────────

    def _fmt_aav(self, res: dict) -> str:
        return (
            f"ID AAV        : {res.get('id_aav', 'N/A')}\n"
            f"Nom           : {res.get('nom', 'N/A')}\n"
            f"Libellé       : {res.get('libelle_integration', 'N/A')}\n"
            f"Discipline    : {res.get('discipline', 'N/A')}\n"
            f"Enseignement  : {res.get('enseignement', 'N/A')}\n"
            f"Type AAV      : {res.get('type_aav', 'N/A')}\n"
            f"Type Éval.    : {res.get('type_evaluation', 'N/A')}\n"
            f"Statut        : {'Actif' if res.get('is_active', True) else 'Inactif'}\n"
            f"Version       : {res.get('version', 'N/A')}\n"
            f"Description   :\n{res.get('description_markdown', 'N/A')}\n"
        )

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    # ─── actions ──────────────────────────────────────────────────────────────

    def rechercher(self, e=None):
        if not self.champ_id.value:
            return
        db = SessionLocal()
        try:
            res = aavs.get_aav(int(self.champ_id.value), db)
            self._set_result(self._fmt_aav(res))
            self.bouton_modifier.visible = True
            self.bouton_supprimer.visible = True
        except Exception as err:
            self._set_result(f"Erreur : AAV #{self.champ_id.value} introuvable\n{err}", "#F44336")
            self.bouton_modifier.visible = False
            self.bouton_supprimer.visible = False
        finally:
            db.close()
            self._page.update()

    def ouvrir_liste(self, e):
        db = SessionLocal()
        try:
            res_list = aavs.get_aavs(db=db)
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
                leading=ft.Icon(ft.Icons.SCHOOL, color="#1565C0"),
                title=ft.Text(f"AAV #{a['id_aav']} — {a.get('nom', '')}", weight="bold"),
                subtitle=ft.Text(f"{a.get('discipline', '')} | {a.get('enseignement', '')}"),
                on_click=lambda e, id_v=a["id_aav"]: selectionner(id_v),
            )
            for a in res_list
        ]
        dialog = ft.AlertDialog(
            title=ft.Text("Liste de toutes les AAVs"),
            content=ft.Container(
                content=ft.ListView(items, spacing=8, padding=10),
                width=520, height=560,
            ),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_creation(self, e):
        champ_nom = ft.TextField(label="Nom", width=420)
        champ_libelle = ft.TextField(label="Libellé Integration", width=420)
        champ_discipline = ft.TextField(label="Discipline", width=420)
        champ_enseignement = ft.TextField(label="Enseignement", width=420)

        def valider(ev):
            db = SessionLocal()
            try:
                donnees = {
                    "nom": champ_nom.value,
                    "libelle_integration": champ_libelle.value,
                    "discipline": champ_discipline.value,
                    "enseignement": champ_enseignement.value,
                }
                res = aavs.create_aav(donnees, db)
                dialog.open = False
                self.champ_id.value = str(res["id_aav"])
                self._page.update()
                self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur création : {err}", "#F44336")
            finally:
                db.close()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer une nouvelle AAV"),
            content=ft.Column([champ_nom, champ_libelle, champ_discipline, champ_enseignement], tight=True),
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
        db = SessionLocal()
        try:
            res = aavs.get_aav(int(self.champ_id.value), db)
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
            db.close()
            return
        db.close()

        champ_nom = ft.TextField(label="Nom", value=res.get("nom", ""), width=420)
        champ_libelle = ft.TextField(label="Libellé Integration", value=res.get("libelle_integration", ""), width=420)
        champ_discipline = ft.TextField(label="Discipline", value=res.get("discipline", ""), width=420)
        champ_enseignement = ft.TextField(label="Enseignement", value=res.get("enseignement", ""), width=420)

        def sauvegarder(ev):
            db2 = SessionLocal()
            try:
                aavs.update_aav(int(self.champ_id.value), {
                    "nom": champ_nom.value,
                    "libelle_integration": champ_libelle.value,
                    "discipline": champ_discipline.value,
                    "enseignement": champ_enseignement.value,
                }, db2)
                self._set_result("✅ AAV modifié avec succès", "#4CAF50")
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                db2.close()
                dialog.open = False
                self._page.update()
                self.rechercher()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier AAV n°{self.champ_id.value}", size=20, weight="bold"),
            content=ft.Column([champ_nom, champ_libelle, champ_discipline, champ_enseignement], scroll=ft.ScrollMode.AUTO),
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
                aavs.delete_aav(int(self.champ_id.value), db)
                self._set_result("✅ AAV supprimé avec succès", "#4CAF50")
                self.bouton_modifier.visible = False
                self.bouton_supprimer.visible = False
            except Exception as err:
                self._set_result(f"❌ Erreur suppression : {err}", "#F44336")
            finally:
                db.close()
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression", weight="bold"),
            content=ft.Text(f"Supprimer AAV #{self.champ_id.value} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="#FFFFFF", bgcolor="#F44336"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    # ─── build ────────────────────────────────────────────────────────────────

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#1565C0"
        COLOR_BG_INPUT = "#E3F2FD"
        COLOR_BORDER = "#2196F3"

        self.champ_id = ft.TextField(
            label="Numéro AAV",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton(
            "Modifier", visible=False, on_click=self.ouvrir_modifier,
            color="#FFFFFF", bgcolor="#2196F3",
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
            border=ft.border.all(1, "#BBDEFB"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("AAVs – Acquis d'Apprentissage Visés", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Voir toutes les AAVs", icon=ft.Icons.LIST, on_click=self.ouvrir_liste, bgcolor="#2196F3", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Nouvelle AAV", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
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
