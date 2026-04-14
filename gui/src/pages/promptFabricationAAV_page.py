"""
Fabrication de Prompts AAV page – style moderne.
CRUD sur les prompts pédagogiques.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class PromptfabricationaavPage:
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

    def _get(self, path):
        r = httpx.get(BASE_URL + path, timeout=5)
        return json.dumps(r.json(), indent=2, ensure_ascii=False)

    def rechercher(self, e=None):
        if not self.champ_id.value:
            return
        try:
            self._set_result(self._get(f"/prompts/{self.champ_id.value}"))
            self.bouton_modifier.visible = True
            self.bouton_supprimer.visible = True
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
            self.bouton_modifier.visible = False
            self.bouton_supprimer.visible = False
        self._page.update()

    def voir_liste(self, e):
        try:
            data = json.loads(self._get("/prompts/"))
            items_raw = data if isinstance(data, list) else data.get("items", [])

            def selectionner(id_v):
                self.champ_id.value = str(id_v)
                dialog.open = False
                self._page.update()
                self.rechercher()

            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.TEXT_SNIPPET, color="#880E4F"),
                    title=ft.Text(f"Prompt #{p.get('id_prompt', p.get('id', '?'))}", weight="bold"),
                    subtitle=ft.Text(str(p.get("contenu", p.get("texte", "")))[:80]),
                    on_click=lambda e, id_v=p.get("id_prompt", p.get("id")): selectionner(id_v),
                )
                for p in items_raw
            ]
            dialog = ft.AlertDialog(
                title=ft.Text("Liste des Prompts"),
                content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
            )
            self._page.overlay.append(dialog)
            dialog.open = True
            self._page.update()
        except Exception as err:
            self._set_result(f"Erreur liste : {err}", "#F44336")

    def ouvrir_creation(self, e):
        champ_aav = ft.TextField(label="ID AAV", keyboard_type=ft.KeyboardType.NUMBER, width=200)
        champ_contenu = ft.TextField(label="Contenu du prompt", width=420, min_lines=4, max_lines=8)

        def valider(ev):
            try:
                body = {"id_aav": int(champ_aav.value) if champ_aav.value else None, "contenu": champ_contenu.value}
                r = httpx.post(BASE_URL + "/prompts/", json=body, timeout=5)
                self._set_result(json.dumps(r.json(), indent=2, ensure_ascii=False))
            except Exception as err:
                self._set_result(f"Erreur création : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer un Prompt"),
            content=ft.Column([champ_aav, champ_contenu], tight=True),
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
        champ_contenu = ft.TextField(label="Nouveau contenu", width=420, min_lines=4, max_lines=8)

        def sauvegarder(ev):
            try:
                r = httpx.patch(BASE_URL + f"/prompts/{self.champ_id.value}", json={"contenu": champ_contenu.value}, timeout=5)
                self._set_result(json.dumps(r.json(), indent=2, ensure_ascii=False))
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier Prompt #{self.champ_id.value}", weight="bold"),
            content=champ_contenu,
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
            try:
                httpx.delete(BASE_URL + f"/prompts/{self.champ_id.value}", timeout=5)
                self._set_result("✅ Prompt supprimé", "#4CAF50")
                self.bouton_modifier.visible = False
                self.bouton_supprimer.visible = False
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression", weight="bold"),
            content=ft.Text(f"Supprimer Prompt #{self.champ_id.value} ?"),
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
        COLOR_PRIMARY = "#880E4F"
        COLOR_BG_INPUT = "#FCE4EC"
        COLOR_BORDER = "#E91E63"

        self.champ_id = ft.TextField(
            label="Numéro Prompt",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton("Modifier", visible=False, on_click=self.ouvrir_modifier, color="#FFFFFF", bgcolor="#E91E63")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="#FFFFFF", bgcolor="#F44336")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#F8BBD9"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Fabrication de Prompts AAV", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Liste des Prompts", icon=ft.Icons.LIST, on_click=self.voir_liste, bgcolor="#AD1457", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Nouveau Prompt", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
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
