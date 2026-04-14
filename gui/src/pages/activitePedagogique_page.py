"""
Activités Pédagogiques page – style moderne.
CRUD activités, gestion des exercices associés, démarrage, soumission, complétion.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class ActivitepedagogiquePage:
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

    def _post(self, path, body=None):
        r = httpx.post(BASE_URL + path, json=body or {}, timeout=5)
        return json.dumps(r.json(), indent=2, ensure_ascii=False)

    def rechercher(self, e=None):
        if not self.champ_id.value:
            return
        try:
            self._set_result(self._get(f"/activities/{self.champ_id.value}"))
            self.bouton_modifier.visible = True
            self.bouton_supprimer.visible = True
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")
            self.bouton_modifier.visible = False
            self.bouton_supprimer.visible = False
        self._page.update()

    def voir_liste(self, e):
        try:
            data = json.loads(self._get("/activities/"))
            items_raw = data if isinstance(data, list) else data.get("items", [])

            def selectionner(id_v):
                self.champ_id.value = str(id_v)
                dialog.open = False
                self._page.update()
                self.rechercher()

            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FITNESS_CENTER, color="#F57F17"),
                    title=ft.Text(f"Activité #{a.get('id', a.get('id_activite', '?'))} — {a.get('titre', a.get('nom', ''))}", weight="bold"),
                    subtitle=ft.Text(str(a.get("type", ""))[:80]),
                    on_click=lambda e, id_v=a.get("id", a.get("id_activite")): selectionner(id_v),
                )
                for a in items_raw
            ]
            dialog = ft.AlertDialog(
                title=ft.Text("Liste des Activités Pédagogiques"),
                content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
            )
            self._page.overlay.append(dialog)
            dialog.open = True
            self._page.update()
        except Exception as err:
            self._set_result(f"Erreur liste : {err}", "#F44336")

    def ouvrir_creation(self, e):
        champ_titre = ft.TextField(label="Titre / Nom", width=400)
        champ_type = ft.TextField(label="Type d'activité", width=400)

        def valider(ev):
            try:
                body = {"titre": champ_titre.value, "type": champ_type.value}
                r = httpx.post(BASE_URL + "/activities/", json=body, timeout=5)
                res = r.json()
                dialog.open = False
                id_key = "id" if "id" in res else "id_activite"
                self.champ_id.value = str(res.get(id_key, ""))
                self._page.update()
                self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur création : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer une Activité Pédagogique"),
            content=ft.Column([champ_titre, champ_type], tight=True),
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
        champ_titre = ft.TextField(label="Titre / Nom", width=400)
        champ_type = ft.TextField(label="Type d'activité", width=400)

        def sauvegarder(ev):
            try:
                r = httpx.put(BASE_URL + f"/activities/{self.champ_id.value}", json={"titre": champ_titre.value, "type": champ_type.value}, timeout=5)
                self._set_result(json.dumps(r.json(), indent=2, ensure_ascii=False))
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier Activité n°{self.champ_id.value}", weight="bold"),
            content=ft.Column([champ_titre, champ_type], scroll=ft.ScrollMode.AUTO),
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
                httpx.delete(BASE_URL + f"/activities/{self.champ_id.value}", timeout=5)
                self._set_result("✅ Activité supprimée", "#4CAF50")
                self.bouton_modifier.visible = False
                self.bouton_supprimer.visible = False
            except Exception as err:
                self._set_result(f"❌ Erreur : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression", weight="bold"),
            content=ft.Text(f"Supprimer Activité #{self.champ_id.value} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="#FFFFFF", bgcolor="#F44336"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def voir_exercices(self, e):
        if not self.champ_id.value:
            return
        try:
            self._set_result(self._get(f"/activities/{self.champ_id.value}/exercises"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def demarrer(self, e):
        if not self.champ_id.value:
            return
        try:
            self._set_result(self._post(f"/activities/{self.champ_id.value}/start"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def completer(self, e):
        if not self.champ_id.value:
            return
        try:
            self._set_result(self._post(f"/activities/{self.champ_id.value}/complete"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#F57F17"
        COLOR_BG_INPUT = "#FFF8E1"
        COLOR_BORDER = "#FFB300"

        self.champ_id = ft.TextField(
            label="Numéro Activité",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.SEARCH,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton("Modifier", visible=False, on_click=self.ouvrir_modifier, color="#FFFFFF", bgcolor="#F9A825")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="#FFFFFF", bgcolor="#F44336")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#FFE082"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Activités Pédagogiques", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Liste Activités", icon=ft.Icons.LIST, on_click=self.voir_liste, bgcolor="#F9A825", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Nouvelle Activité", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Row([
                        ft.ElevatedButton("Voir Exercices", icon=ft.Icons.FITNESS_CENTER, on_click=self.voir_exercices, bgcolor="#0288D1", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Démarrer", icon=ft.Icons.PLAY_ARROW, on_click=self.demarrer, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Compléter", icon=ft.Icons.CHECK_CIRCLE, on_click=self.completer, bgcolor="#43A047", color=ft.Colors.WHITE),
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
