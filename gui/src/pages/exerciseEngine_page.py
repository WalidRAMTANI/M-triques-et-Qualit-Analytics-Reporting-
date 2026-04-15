import sys
import json
import httpx
import flet as ft
from pathlib import Path
from typing import Optional

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class ExerciseenginePage:
    """
    Page de pilotage du moteur d'exercices et des regles de progression.
    Permet de consulter les prompts, les regles de passage et de generer des sequences adaptatives.
    """

    def __init__(self, content_area):
        """Initialise les references de conteneur d'affichage et les elements de champ."""
        self.content_area = content_area
        self._page = None
        self.champ_aav = None
        self.champ_apprenant = None
        self.champ_prompt = None
        self.result_container = None

    def _set_result_content(self, control: ft.Control):
        """Met a jour le contenu de la zone de resultats."""
        self.result_container.content = control
        if self._page:
            self._page.update()

    def _set_error(self, msg: str):
        """Affiche un message d'erreur structure dans la zone de resultats."""
        self._set_result_content(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.WHITE, size=28),
                    ft.Text(msg, color=ft.Colors.WHITE, size=15, weight="w500", expand=True)
                ]),
                bgcolor="#EF5350",
                border_radius=12,
                padding=20
            )
        )

    def _handle_response(self, response: httpx.Response, success_msg: str = None) -> bool:
        """Traite les retours HTTP et gere l'affichage des succes ou echecs."""
        if response.status_code in [200, 201]:
            if success_msg:
                self._set_result_content(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.WHITE, size=28),
                            ft.Text(success_msg, color=ft.Colors.WHITE, size=15, weight="bold")
                        ]),
                        bgcolor="#66BB6A",
                        border_radius=12,
                        padding=20
                    )
                )
            return True
        
        msg = f"Erreur {response.status_code}"
        if response.status_code == 404:
            msg = "Donnees introuvables."
        elif response.status_code == 422:
            msg = "Echec de validation des parametres."
            
        try:
            detail = response.json().get("detail")
            if detail: msg += f" - {detail}"
        except: pass

        self._set_error(msg)
        return False

    def _format_value(self, v):
        """Formate recursivement les donnees API pour un affichage texte lisible."""
        if v is None:
            return "---"
        if isinstance(v, list):
            if not v:
                return "Aucun element."
            return ", ".join(str(i) for i in v)
        if isinstance(v, dict):
            if not v:
                return "Vide."
            res = ""
            for sub_k, sub_v in v.items():
                res += f"- {str(sub_k).capitalize()}: {self._format_value(sub_v)}\n"
            return res.strip()
        return str(v)

    def _dict_to_ui(self, data: dict, title: str, icon: str = ft.Icons.SETTINGS):
        """Convertit un dictionnaire de donnees en une carte graphique detaillee."""
        rows = []
        for k, v in data.items():
            k_clean = str(k).replace("_", " ").title()
            val_str = self._format_value(v)
            rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{k_clean}", weight="w600", color="#004D40", size=14, width=170),
                        ft.Text(val_str, color="#424242", size=14, expand=True, selectable=True)
                    ], vertical_alignment=ft.CrossAxisAlignment.START),
                    padding=ft.padding.symmetric(vertical=12, horizontal=8),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, "#EEEEEE"))
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color="#004D40", size=24),
                    ft.Text(title, size=20, weight="bold", color="#004D40"),
                ]),
                ft.Divider(color="#E0F2F1", height=20),
                *rows
            ], scroll=ft.ScrollMode.AUTO),
            padding=24,
            bgcolor="#FFFFFF",
            border_radius=16
        )
        
    def _list_to_ui(self, data_list: list, title: str, icon: str = ft.Icons.LIST):
        """Convertit une liste d'entites en une suite de cartes visuelles legere."""
        if not data_list:
            return self._dict_to_ui({"Statut": "Pas de donnee."}, title, icon)
            
        rows = []
        for item in data_list:
            content_str = self._format_value(item)
            rows.append(
                ft.Container(
                    content=ft.Text(content_str, color="#424242", size=14, selectable=True),
                    padding=16,
                    margin=ft.margin.only(bottom=10),
                    bgcolor="#FAFAFA",
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=8
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color="#004D40", size=24),
                    ft.Text(title, size=20, weight="bold", color="#004D40"),
                    ft.Text(f"({len(data_list)} items)", size=14, color="#757575")
                ]),
                ft.Divider(color="#E0F2F1", height=20),
                *rows
            ], scroll=ft.ScrollMode.AUTO),
            padding=24,
            bgcolor="#FFFFFF",
            border_radius=16
        )

    def _get_int(self, field) -> Optional[int]:
        """Extrait de maniere securisee un entier depuis un champ de texte."""
        if not field.value or not field.value.strip():
            return None
        try:
            return int(field.value.strip())
        except ValueError:
            return None

    def voir_prompts_aav(self, e):
        """Recupere la liste des prompts associes a un AAV specifique."""
        id_aav = self._get_int(self.champ_aav)
        if id_aav is None:
            self._set_error("ID AAV requis.")
            return
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            r = httpx.get(f"{BASE_URL}/aavs/{id_aav}/prompts", timeout=10)
            if self._handle_response(r):
                data = r.json()
                self._set_result_content(self._list_to_ui(data, f"Prompts AAV #{id_aav}", ft.Icons.TEXT_SNIPPET))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def voir_regles(self, e):
        """Consulte l'ensemble des regles de progression globales."""
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            r = httpx.get(f"{BASE_URL}/progression-rules", timeout=10)
            if self._handle_response(r):
                data = r.json()
                self._set_result_content(self._list_to_ui(data, "Regles Globales", ft.Icons.RULE))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def voir_regles_aav(self, e):
        """Affiche les regles de passage specifiques a un AAV."""
        id_aav = self._get_int(self.champ_aav)
        if id_aav is None:
            self._set_error("ID AAV requis.")
            return
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            r = httpx.get(f"{BASE_URL}/progression-rules/{id_aav}", timeout=10)
            if self._handle_response(r):
                self._set_result_content(self._dict_to_ui(r.json(), f"Regles AAV #{id_aav}", ft.Icons.RULE_FOLDER))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def prochain_exercice(self, e):
        """Interroge le moteur pour obtenir la recommandation du prochain exercice a effectuer."""
        id_aav = self._get_int(self.champ_aav)
        if id_aav is None:
            self._set_error("ID AAV requis.")
            return
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            params = {}
            id_app = self._get_int(self.champ_apprenant)
            if id_app is not None: params["id_apprenant"] = id_app
            r = httpx.get(f"{BASE_URL}/next-exercise/{id_aav}", params=params, timeout=10)
            if self._handle_response(r):
                self._set_result_content(self._dict_to_ui(r.json(), "Prochain Exercice", ft.Icons.ARROW_FORWARD))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def voir_sequence(self, e):
        """Genere une sequence d'apprentissage complete pour un couple Apprenant/AAV."""
        id_app = self._get_int(self.champ_apprenant)
        id_aav = self._get_int(self.champ_aav)
        if id_app is None or id_aav is None:
            self._set_error("ID Apprenant et AAV requis.")
            return
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            r = httpx.get(f"{BASE_URL}/sequence/{id_app}/{id_aav}", timeout=10)
            if self._handle_response(r):
                data = r.json()
                self._set_result_content(self._list_to_ui(data, f"Sequence AAV #{id_aav}", ft.Icons.PLAYLIST_PLAY))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def preview_prompt(self, e):
        """Simule le rendu d'un prompt compile avec le contexte d'un apprenant."""
        id_p = self._get_int(self.champ_prompt)
        id_app = self._get_int(self.champ_apprenant)
        if id_p is None or id_app is None:
            self._set_error("ID Prompt et Apprenant requis.")
            return
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            r = httpx.post(f"{BASE_URL}/prompts/{id_p}/preview", json={"id_apprenant": id_app, "include_context": True}, timeout=15)
            if self._handle_response(r):
                self._set_result_content(self._dict_to_ui(r.json(), "Apercu Prompt", ft.Icons.PREVIEW))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def taux_succes_prompt(self, e):
        """Analyse le taux de reussite historique associe a un prompt pedagogique."""
        id_p = self._get_int(self.champ_prompt)
        if id_p is None:
            self._set_error("ID Prompt requis.")
            return
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            r = httpx.get(f"{BASE_URL}/prompts/{id_p}/success-rate", timeout=10)
            if self._handle_response(r):
                self._set_result_content(self._dict_to_ui(r.json(), "Statistiques de Succes", ft.Icons.ANALYTICS))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def selectionner_exercices(self, e):
        """Active l'algorithme de selection intelligente pour un set d'exercices adaptatifs."""
        id_app = self._get_int(self.champ_apprenant)
        id_aav = self._get_int(self.champ_aav)
        if id_app is None or id_aav is None:
            self._set_error("Parametres manquants.")
            return
        self._set_result_content(ft.ProgressRing(color="#00695C"))
        try:
            payload = {"id_apprenant": id_app, "id_aavs_cibles": [id_aav], "strategie": "adaptive", "nombre_exercices": 3}
            r = httpx.post(f"{BASE_URL}/exercises/select", json=payload, timeout=15)
            if self._handle_response(r):
                self._set_result_content(self._list_to_ui(r.json(), "Selection Adaptive", ft.Icons.CHECKLIST))
        except Exception as err:
            self._set_error(f"Erreur : {err}")

    def build(self, page: ft.Page):
        """Construit l'interface graphique de la page du moteur."""
        self._page = page
        
        def input_field(label, icon):
            return ft.TextField(label=label, width=200, keyboard_type=ft.KeyboardType.NUMBER, border_radius=12,
                                border_color="#009688", bgcolor="white", prefix_icon=icon)

        self.champ_aav = input_field("ID AAV", ft.Icons.SCHOOL)
        self.champ_apprenant = input_field("ID Apprenant", ft.Icons.PERSON)
        self.champ_prompt = input_field("ID Prompt", ft.Icons.TEXT_SNIPPET)

        self.result_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.TUNE, size=60, color="#B2DFDB"),
                ft.Text("Parametrez les IDs et lancez une analyse.", color="#00897B")
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=800, height=300, bgcolor="#FFFFFF", border_radius=16, padding=20
        )

        def btn(icon, text, handler, bg):
            return ft.ElevatedButton(text, icon=icon, on_click=handler, color="white", bgcolor=bg)

        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SETTINGS_APPLICATIONS, size=40, color="#004D40"),
                ft.Text("Moteur d'Exercices et Progression", size=24, weight="bold", color="#004D40"),
            ]),
            margin=ft.margin.only(bottom=20)
        )

        return ft.Container(
            content=ft.Column([
                header,
                ft.Container(
                    content=ft.Column([
                        ft.Row([self.champ_aav, self.champ_apprenant, self.champ_prompt], wrap=True),
                        ft.Text("Algorithmes et Regles", weight="bold"),
                        ft.Row([
                            btn(ft.Icons.RULE, "Regles Globales", self.voir_regles, "#004D40"),
                            btn(ft.Icons.RULE_FOLDER, "Regles AAV", self.voir_regles_aav, "#00695C"),
                            btn(ft.Icons.ARROW_FORWARD, "Prochain Ex.", self.prochain_exercice, "#00796B"),
                            btn(ft.Icons.PLAYLIST_PLAY, "Sequence", self.voir_sequence, "#00897B"),
                        ], wrap=True),
                        ft.Text("Gestion des Prompts", weight="bold"),
                        ft.Row([
                            btn(ft.Icons.TEXT_SNIPPET, "Prompts AAV", self.voir_prompts_aav, "#26A69A"),
                            btn(ft.Icons.PREVIEW, "Apercu Prompt", self.preview_prompt, "#4DB6AC"),
                            btn(ft.Icons.ANALYTICS, "Succes Rate", self.taux_succes_prompt, "#F9A825"),
                            btn(ft.Icons.CHECKLIST, "Select. Auto", self.selectionner_exercices, "#0288D1"),
                        ], wrap=True),
                    ], spacing=15),
                    bgcolor="#FFFFFF", padding=24, border_radius=16
                ),
                self.result_container
            ], scroll=ft.ScrollMode.AUTO),
            padding=30, expand=True, bgcolor="#F4FDFB"
        )
