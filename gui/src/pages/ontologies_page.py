import sys
import json
import requests
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class OntologiesPage:
    """
    Page de gestion des ontologies de reference.
    Permet de consulter, creer, modifier et supprimer les structures ontologiques.
    """

    def __init__(self, content_area, is_professor=False):
        """Initialise la page avec les permissions utilisateur et les references d'affichage."""
        self.content_area = content_area
        self.is_professor = is_professor
        self._page = None
        self.champ_id = None
        self.result_container = None
        self.bouton_modifier = None
        self.bouton_supprimer = None

    def _set_result_content(self, control: ft.Control):
        """Met a jour la zone de resultats centrale."""
        self.result_container.content = control
        if self._page:
            self._page.update()

    def _set_error(self, msg: str):
        """Affiche un message d'erreur structure."""
        self._set_result_content(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.WHITE, size=28),
                    ft.Text(msg, color=ft.Colors.WHITE, size=15, weight="w500", expand=True)
                ]),
                bgcolor="#EF5350", border_radius=12, padding=20
            )
        )

    def _handle_response(self, response: requests.Response, success_msg: str = None) -> bool:
        """Gere les retours de l'API et affiche les notifications appropriees."""
        if response.status_code in [200, 201, 204]:
            if success_msg:
                self._set_result_content(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.WHITE, size=28),
                            ft.Text(success_msg, color=ft.Colors.WHITE, size=15, weight="bold")
                        ]),
                        bgcolor="#66BB6A", border_radius=12, padding=20
                    )
                )
            return True
        
        msg = f"Erreur {response.status_code}"
        if response.status_code == 404:
            msg = "Ontologie introuvable."
        elif response.status_code == 400:
            msg = "Donnees invalides."
        
        try:
            detail = response.json().get("detail")
            if detail: msg += f" - {detail}"
        except: pass

        self._set_error(msg)
        return False

    def _format_value(self, v):
        """Formate recursivement les valeurs complexes pour l'affichage textuel."""
        if v is None:
            return "---"
        if isinstance(v, list):
            if not v:
                return "Aucun element."
            if all(isinstance(i, dict) for i in v):
                res = ""
                for idx, item in enumerate(v):
                    res += f"- Element {idx+1} :\n"
                    for sub_k, sub_v in item.items():
                        res += f"      {str(sub_k).replace('_', ' ').capitalize()}: {sub_v}\n"
                return res.strip()
            return ", ".join(str(i) for i in v)
        if isinstance(v, dict):
            if not v:
                return "Aucune information."
            res = ""
            for sub_k, sub_v in v.items():
                res += f"* {str(sub_k).replace('_', ' ').capitalize()}: {self._format_value(sub_v)}\n"
            return res.strip()
        return str(v)

    def _dict_to_ui(self, data: dict, title="Details Ontologie"):
        """Convertit un dictionnaire de donnees en composants UI structures."""
        rows = []
        for k, v in data.items():
            k_clean = str(k).replace("_", " ").title()
            val_str = self._format_value(v)
            rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{k_clean}", weight="w600", color="#4A148C", size=14, width=170),
                        ft.Text(val_str, color="#424242", size=14, expand=True, selectable=True)
                    ], vertical_alignment=ft.CrossAxisAlignment.START),
                    padding=ft.padding.symmetric(vertical=12, horizontal=8),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, "#EEEEEE"))
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_TREE, color="#4A148C", size=24),
                    ft.Text(title, size=20, weight="bold", color="#4A148C"),
                ]),
                ft.Divider(color="#F3E5F5", height=20),
                *rows
            ], scroll=ft.ScrollMode.AUTO),
            padding=24, bgcolor="#FFFFFF", border_radius=16
        )

    def rechercher(self, e=None):
        """Recherche une ontologie par son identifiant unique."""
        if not self.champ_id.value:
            self._set_error("ID requis.")
            return
            
        self._set_result_content(ft.ProgressRing(color="#7B1FA2"))
        try:
            response = requests.get(f"http://127.0.0.1:8000/ontologies/{int(self.champ_id.value)}")
            if self._handle_response(response):
                data = response.json()
                self._set_result_content(self._dict_to_ui(data, title=f"Ontologie #{self.champ_id.value} : {data.get('discipline', '')}"))
                self.secure_set_visible(self.bouton_modifier, True)
                self.secure_set_visible(self.bouton_supprimer, True)
            else:
                self.secure_set_visible(self.bouton_modifier, False)
                self.secure_set_visible(self.bouton_supprimer, False)
        except Exception as err:
            self._set_error(f"Erreur : {err}")
        finally:
            self._page.update()

    def ouvrir_liste(self, e):
        """Affiche la liste complete des ontologies dans un dialogue modal."""
        self._set_result_content(ft.ProgressRing(color="#7B1FA2"))
        try:
            response = requests.get("http://127.0.0.1:8000/ontologies/")
            if not self._handle_response(response): return
            res_list = response.json()
        except:
            self._set_error("Serveur inaccessible.")
            return
            
        if not res_list:
            self._set_result_content(ft.Container(ft.Text("Liste vide."), padding=20))
            return

        def selectionner(id_v):
            self.champ_id.value = str(id_v)
            dialog.open = False
            self._page.update()
            self.rechercher()

        cards = []
        for o in res_list:
            id_val = o.get('id_reference', o.get('id', '?'))
            card = ft.Container(
                content=ft.ListTile(
                    leading=ft.CircleAvatar(content=ft.Icon(ft.Icons.ACCOUNT_TREE), bgcolor="#F3E5F5", color="#4A148C"),
                    title=ft.Text(f"#{id_val} - {o.get('discipline', '')}", weight="bold"),
                    subtitle=ft.Text(str(o.get("description", ""))[:80] + "..."),
                    on_click=lambda e, idx=id_val: selectionner(idx),
                ),
                border_radius=8, bgcolor="#FAFAFA", border=ft.border.all(1, "#E0E0E0"), margin=ft.margin.only(bottom=8)
            )
            cards.append(card)

        dialog = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.Icons.DYNAMIC_FEED, color="#4A148C"), ft.Text("Referentiel Ontologique")]),
            content=ft.Container(content=ft.ListView(cards, padding=10), width=450, height=450),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_creation(self, e):
        """Ouvre un formulaire de creation d'une nouvelle ontologie."""
        champ_nom = ft.TextField(label="Discipline", width=420)
        champ_desc = ft.TextField(label="Description", width=420, min_lines=3, max_lines=5)

        def valider(ev):
            try:
                response = requests.post("http://127.0.0.1:8000/ontologies/", json={"discipline": champ_nom.value, "description": champ_desc.value})
                if self._handle_response(response, "Ontologie creee."):
                    res = response.json()
                    dialog.open = False
                    self.champ_id.value = str(res.get("id_reference", ""))
                    self._page.update()
                    self.rechercher()
            except Exception as err:
                self._set_error(f"Erreur : {err}")

        dialog = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.Icons.ADD_BOX, color="#4CAF50"), ft.Text("Nouvelle Ontologie")]),
            content=ft.Column([champ_nom, champ_desc], tight=True, spacing=15),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Creer", on_click=valider, bgcolor="#4CAF50", color="white"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_modifier(self, e):
        """Ouvre un formulaire pour modifier l'ontologie selectionnee."""
        if not self.champ_id.value: return
        champ_nom = ft.TextField(label="Discipline", width=420)
        champ_desc = ft.TextField(label="Description", width=420, min_lines=3, max_lines=5)

        def sauvegarder(ev):
            try:
                response = requests.put(f"http://127.0.0.1:8000/ontologies/{int(self.champ_id.value)}", json={"discipline": champ_nom.value, "description": champ_desc.value})
                if self._handle_response(response, "Modifications enregistrees."):
                    self.rechercher()
            except Exception as err:
                self._set_error(f"Erreur : {err}")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.Icons.EDIT, color="#FF9800"), ft.Text(f"Modifier #{self.champ_id.value}")]),
            content=ft.Column([champ_nom, champ_desc], tight=True, spacing=15),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Sauvegarder", on_click=sauvegarder, color="white", bgcolor="#FF9800"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def action_supprimer(self, e):
        """Demande confirmation avant de supprimer l'ontologie."""
        if not self.champ_id.value: return

        def confirmer(ev):
            try:
                response = requests.delete(f"http://127.0.0.1:8000/ontologies/{int(self.champ_id.value)}")
                if self._handle_response(response, "Ontologie supprimee."):
                    self.secure_set_visible(self.bouton_modifier, False)
                    self.secure_set_visible(self.bouton_supprimer, False)
                    self.champ_id.value = ""
            except Exception as err:
                self._set_error(f"Erreur : {err}")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.Icons.WARNING_AMBER, color="#F44336"), ft.Text("Confirmation")]),
            content=ft.Text(f"Supprimer l'ontologie #{self.champ_id.value} ? Cette action est irreversible."),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="white", bgcolor="#F44336"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def build(self, page: ft.Page):
        """Genere le rendu visuel de la page des ontologies."""
        self._page = page
        COLOR_PRIMARY = "#4A148C"

        self.champ_id = ft.TextField(
            label="ID Ontologie", width=220, keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=12, border_color="#7B1FA2", bgcolor="#FFFFFF",
            prefix_icon=ft.Icons.ACCOUNT_TREE_OUTLINED, height=60
        )
        
        self.result_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.HUB, size=60, color="#E1BEE7"),
                ft.Text("Selectionnez une ontologie pour afficher les details.", color="#BA68C8", text_align="center")
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=800, height=450, bgcolor="#FFFFFF", border_radius=16, padding=20, border=ft.border.all(1, "#F3E5F5")
        )

        self.bouton_modifier = ft.ElevatedButton("Modifier", icon=ft.Icons.EDIT, visible=False, on_click=self.ouvrir_modifier, color="white", bgcolor="#FFB300")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", icon=ft.Icons.DELETE, visible=False, on_click=self.action_supprimer, color="white", bgcolor="#E53935")

        def secure_set_visible(btn, val):
            btn.visible = val if self.is_professor else False
        self.secure_set_visible = secure_set_visible

        def _action_btn(icon, text, click_handler, bg):
            return ft.ElevatedButton(text, icon=icon, on_click=click_handler, color="white", bgcolor=bg, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))

        header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.Icons.HUB, size=40, color="#FFFFFF"), padding=16, bgcolor=COLOR_PRIMARY, border_radius=16),
                ft.Column([
                    ft.Text("Ontologies de Reference", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Text("Gestion des concepts theoriques et structures disciplinaires.", size=14),
                ])
            ]), margin=ft.margin.only(bottom=30)
        )

        controls = ft.Container(
            content=ft.Row([
                self.champ_id,
                _action_btn(ft.Icons.SEARCH, "Chercher", self.rechercher, COLOR_PRIMARY),
                _action_btn(ft.Icons.LIST, "Tout parcourir", self.ouvrir_liste, "#7B1FA2"),
                _action_btn(ft.Icons.ADD, "Nouveau", self.ouvrir_creation, "#43A047") if self.is_professor else ft.Container(),
            ], wrap=True, alignment=ft.MainAxisAlignment.START),
            padding=24, bgcolor="#FFFFFF", border_radius=16
        )

        return ft.Container(
            content=ft.Column([
                header, controls, self.result_container,
                ft.Row([self.bouton_modifier, self.bouton_supprimer], alignment=ft.MainAxisAlignment.END, spacing=15)
            ], horizontal_alignment=ft.CrossAxisAlignment.STRETCH, scroll=ft.ScrollMode.AUTO),
            bgcolor="#FAFAFA", expand=True, padding=40
        )
