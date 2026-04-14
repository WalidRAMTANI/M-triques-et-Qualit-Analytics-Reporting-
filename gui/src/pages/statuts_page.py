"""
Statuts d'Apprentissage page – style moderne.
Recherche, CRUD et gestion de la maîtrise des AAVs par apprenant.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class StatutsPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_modifier = None
        self.bouton_reset = None

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
            self._set_result(self._get(f"/learning-status/{self.champ_id.value}"))
            self.bouton_modifier.visible = True
            self.bouton_reset.visible = True
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
            self.bouton_modifier.visible = False
            self.bouton_reset.visible = False
        self._page.update()

    def voir_liste(self, e):
        try:
            data = json.loads(self._get("/learning-status"))
            items_raw = data if isinstance(data, list) else []

            def selectionner(id_v):
                self.champ_id.value = str(id_v)
                dialog.open = False
                self._page.update()
                self.rechercher()

            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.BOOKMARK, color="#1565C0"),
                    title=ft.Text(f"Statut #{s.get('id_statut', s.get('id', '?'))}", weight="bold"),
                    subtitle=ft.Text(f"AAV: {s.get('id_aav', 'N/A')} | Maîtrise: {s.get('niveau_maitrise', 'N/A')}"),
                    on_click=lambda e, id_v=s.get("id_statut", s.get("id")): selectionner(id_v),
                )
                for s in items_raw
            ]
            dialog = ft.AlertDialog(
                title=ft.Text("Liste des Statuts d'Apprentissage"),
                content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
            )
            self._page.overlay.append(dialog)
            dialog.open = True
            self._page.update()
        except Exception as err:
            self._set_result(f"Erreur liste : {err}", "#F44336")

    def ouvrir_modifier(self, e):
        if not self.champ_id.value:
            return
        champ_niveau = ft.TextField(label="Nouveau niveau de maîtrise", width=300)

        def sauvegarder(ev):
            try:
                body = {"niveau_maitrise": champ_niveau.value}
                r = httpx.patch(BASE_URL + f"/learning-status/{self.champ_id.value}/mastery", json=body, timeout=5)
                self._set_result(json.dumps(r.json(), indent=2, ensure_ascii=False))
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Mettre à jour la maîtrise – Statut #{self.champ_id.value}", weight="bold"),
            content=champ_niveau,
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Sauvegarder", on_click=sauvegarder, color="#FFFFFF", bgcolor="#4CAF50"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def reset(self, e):
        if not self.champ_id.value:
            return
        try:
            r = httpx.post(BASE_URL + f"/learning-status/{self.champ_id.value}/reset", timeout=5)
            self._set_result(f"✅ Réinitialisation\n{json.dumps(r.json(), indent=2, ensure_ascii=False)}", "#4CAF50")
        except Exception as err:
            self._set_result(f"❌ Erreur reset : {err}", "#F44336")

    def voir_tentatives(self, e):
        if not self.champ_id.value:
            return
        try:
            self._set_result(self._get(f"/learning-status/{self.champ_id.value}/attempts"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#1565C0"
        COLOR_BG_INPUT = "#E3F2FD"
        COLOR_BORDER = "#2196F3"

        self.champ_id = ft.TextField(
            label="Numéro Statut",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton("Modifier Maîtrise", visible=False, on_click=self.ouvrir_modifier, color="#FFFFFF", bgcolor="#2196F3")
        self.bouton_reset = ft.ElevatedButton("Réinitialiser", visible=False, on_click=self.reset, color="#FFFFFF", bgcolor=ft.Colors.AMBER_700)

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
                    ft.Text("Statuts d'Apprentissage", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Liste Globale", icon=ft.Icons.LIST, on_click=self.voir_liste, bgcolor="#1976D2", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Tentatives", icon=ft.Icons.HISTORY, on_click=self.voir_tentatives, bgcolor=ft.Colors.AMBER_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([self.bouton_modifier, self.bouton_reset], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
