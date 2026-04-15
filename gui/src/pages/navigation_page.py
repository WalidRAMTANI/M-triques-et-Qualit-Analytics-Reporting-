import sys
import flet as ft
import httpx
from pathlib import Path
from typing import Optional

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class NavigationPage:
    """
    Page d'exploration des parcours de navigation pour les apprenants.
    Permet de visualiser dynamiquement l'etat des AAV selon leur disponibilite pedagogique.
    """

    def __init__(self, content_area):
        """Initialise la page avec les conteneurs d'affichage et de saisie d'identifiants."""
        self.content_area = content_area
        self._page = None
        self.champ_id = None
        self.result_container = None

    def _set_result_content(self, control: ft.Control):
        """Met a jour le conteneur principal de resultats avec un nouveau composant UI."""
        self.result_container.content = control
        if self._page: self._page.update()

    def _set_error(self, msg: str):
        """Affiche un message d'erreur standardise dans la zone de contenu."""
        self._set_result_content(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color="white", size=28),
                    ft.Text(msg, color="white", size=15, weight="w500", expand=True)
                ]),
                bgcolor="#EF5350", border_radius=12, padding=20
            )
        )

    def _format_value(self, v):
        """Formate recursivement les donnees complexes pour un affichage textuel structure."""
        if v is None: return "Non renseigne."
        if isinstance(v, list):
            if not v: return "Aucune donnee repertoriee."
            if all(isinstance(i, dict) for i in v):
                res = ""
                for idx, item in enumerate(v):
                    res += f"Entree {idx+1} :\n"
                    for sub_k, sub_v in item.items():
                        res += f"      {str(sub_k).replace('_', ' ').capitalize()}: {sub_v}\n"
                return res.strip()
            return ", ".join(map(str, v))
        if isinstance(v, dict):
            if not v: return "Metadata vides."
            return "\n".join([f"- {str(sub_k).replace('_', ' ').capitalize()}: {self._format_value(sub_v)}" for sub_k, sub_v in v.items()])
        return str(v)

    def _dict_to_ui(self, data: dict, title: str, icon: str):
        """Transforme un dictionnaire de donnees en une vue detaillee structuree."""
        rows = [
            ft.Container(
                content=ft.Row([
                    ft.Text(str(k).replace("_", " ").title(), weight="w600", color="#1B5E20", size=14, width=200),
                    ft.Text(self._format_value(v), color="#424242", size=14, expand=True, selectable=True)
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                padding=ft.padding.symmetric(vertical=12, horizontal=8),
                border=ft.border.only(bottom=ft.border.BorderSide(1, "#EEEEEE"))
            )
            for k, v in data.items()
        ]
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color="#1B5E20", size=24), ft.Text(title, size=20, weight="bold", color="#1B5E20")]),
                ft.Divider(color="#E8F5E9", height=20),
                *rows
            ], scroll=ft.ScrollMode.AUTO),
            padding=24, bgcolor="#FFFFFF", border_radius=16,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK))
        )

    def _list_to_ui(self, data_list: list, title: str, icon: str):
        """Transforme une liste de donnees en une vue en liste d'elements interactifs."""
        if not data_list: return self._dict_to_ui({"Statut": "Liste de navigation vide."}, title, icon)
        rows = [
            ft.Container(
                content=ft.Text(self._format_value(item), color="#424242", size=14, selectable=True),
                padding=16, margin=ft.margin.only(bottom=10), bgcolor="#FAFAFA",
                border=ft.border.all(1, "#E0E0E0"), border_radius=8
            )
            for item in data_list
        ]
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color="#1B5E20", size=24), ft.Text(title, size=20, weight="bold", color="#1B5E20"), ft.Text(f"({len(data_list)} elements)", size=14, color="#757575")]),
                ft.Divider(color="#E8F5E9", height=20),
                *rows
            ], scroll=ft.ScrollMode.AUTO),
            padding=24, bgcolor="#FFFFFF", border_radius=16,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK))
        )

    def _get_data(self, path: str, title: str, icon: str):
        """Interroge l'API et oriente les donnees vers le constructeur UI approprie."""
        self._set_result_content(ft.ProgressRing(color="#4CAF50"))
        try:
            r = httpx.get(BASE_URL + path, timeout=10)
            if r.status_code in [200, 201]:
                data = r.json()
                if isinstance(data, dict): self._set_result_content(self._dict_to_ui(data, title, icon))
                elif isinstance(data, list): self._set_result_content(self._list_to_ui(data, title, icon))
                else: self._set_result_content(self._dict_to_ui({"Donnee": data}, title, icon))
            else:
                self._set_error(f"Echec de la requete ({r.status_code}).")
        except Exception as err:
            self._set_error(f"Connexion au serveur impossible : {err}")

    def _require_id(self) -> Optional[str]:
        """Assure la presence de l'identifiant apprenant avant toute action API."""
        if not self.champ_id.value or not str(self.champ_id.value).strip():
            self._set_error("Veuillez saisir un numero d'apprenant valide.")
            return None
        return str(self.champ_id.value).strip()

    def voir_accessibles(self, e):
        """Affiche les AAV dont les prerequis sont satisfaits et qui sont disponibles."""
        if id_v := self._require_id():
            self._get_data(f"/navigation/{id_v}/accessible", f"AAV Accessibles - Apprenant #{id_v}", ft.Icons.LOCK_OPEN)

    def voir_en_cours(self, e):
        """Affiche les AAV actuellement inities mais non valides pour l'apprenant."""
        if id_v := self._require_id():
            self._get_data(f"/navigation/{id_v}/in-progress", f"AAV En Cours - Apprenant #{id_v}", ft.Icons.PLAY_ARROW)

    def voir_bloquees(self, e):
        """Affiche les AAV inaccessibles en raison de prerequis non valides."""
        if id_v := self._require_id():
            self._get_data(f"/navigation/{id_v}/blocked", f"AAV Bloquees - Apprenant #{id_v}", ft.Icons.LOCK)

    def voir_revisables(self, e):
        """Affiche les AAV valides mais suggeres pour une revision academique."""
        if id_v := self._require_id():
            self._get_data(f"/navigation/{id_v}/reviewable", f"AAV a Reviser - Apprenant #{id_v}", ft.Icons.REFRESH)

    def voir_dashboard(self, e):
        """Genere une vue syntheticale des metadonnees de navigation de l'apprenant."""
        if id_v := self._require_id():
            self._get_data(f"/navigation/{id_v}/dashboard", f"Status General - Apprenant #{id_v}", ft.Icons.DASHBOARD)

    def voir_tout(self, e):
        """Affiche l'integralite du graphe de navigation pour un profil donne."""
        if id_v := self._require_id():
            self._get_data(f"/navigation/{id_v}", f"Dossier de Navigation - Apprenant #{id_v}", ft.Icons.LIST_ALT)

    def build(self, page: ft.Page):
        """Construit l'interface premium de consultation des parcours de navigation."""
        self._page = page
        cor_prim, cor_sec, cor_bg = "#1B5E20", "#4CAF50", "#F1F8E9"

        self.champ_id = ft.TextField(
            label="Identifiant Apprenant", width=220, keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=12, border_color=cor_sec, bgcolor="white",
            prefix_icon=ft.Icons.PERSON, cursor_color=cor_prim, height=60
        )
        
        self.result_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ROUTE, size=60, color="#A5D6A7"),
                ft.Text("Veuillez selectionner une categorie d'analyse.", color="#81C784", size=15)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=800, height=450, bgcolor="white", border_radius=16, padding=20,
            border=ft.border.all(1, "#E8F5E9"), alignment=ft.Alignment(0, 0)
        )

        def _action_btn(icon, text, click_handler, bg):
            return ft.ElevatedButton(
                text, icon=icon, on_click=click_handler, color="white", bgcolor=bg,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12), padding=ft.padding.symmetric(horizontal=24, vertical=16))
            )

        header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Icon(ft.Icons.EXPLORE, size=40, color="white"), padding=16, bgcolor=cor_prim, border_radius=16),
                ft.Column([
                    ft.Text("Navigation et Parcours", size=28, weight="bold", color=cor_prim),
                    ft.Text("Analyse systemique de l'accessibilite des ressources pedagogiques.", size=14, color="#388E3C"),
                ], spacing=2)
            ]), margin=ft.margin.only(bottom=30)
        )

        row1 = ft.Row([
            _action_btn(ft.Icons.LOCK_OPEN, "Accessibles", self.voir_accessibles, cor_prim),
            _action_btn(ft.Icons.PLAY_ARROW, "En cours", self.voir_en_cours, "#2E7D32"),
            _action_btn(ft.Icons.LOCK, "Bloquees", self.voir_bloquees, "#D32F2F"),
        ], spacing=15, wrap=True)
        
        row2 = ft.Row([
            _action_btn(ft.Icons.REFRESH, "A reviser", self.voir_revisables, "#F57C00"),
            _action_btn(ft.Icons.DASHBOARD, "Dashboard", self.voir_dashboard, "#0288D1"),
            _action_btn(ft.Icons.LIST, "Vues globales", self.voir_tout, "#455A64"),
        ], spacing=15, wrap=True)

        return ft.Container(
            content=ft.Column([
                header,
                ft.Container(
                    content=ft.Column([ft.Row([self.champ_id]), ft.Divider(height=10, color="transparent"), row1, row2], spacing=15),
                    bgcolor="white", padding=24, border_radius=16, margin=ft.margin.only(bottom=20)
                ),
                self.result_container,
            ], horizontal_alignment=ft.CrossAxisAlignment.STRETCH, scroll=ft.ScrollMode.AUTO),
            bgcolor=cor_bg, expand=True, padding=ft.padding.all(40)
        )
