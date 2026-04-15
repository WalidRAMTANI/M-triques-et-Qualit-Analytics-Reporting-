import sys
import flet as ft
import httpx
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class ComparaisonPage:
    """
    Page d'analyse comparative des performances.
    Permet de confronter les metriques entre differents AAV ou entre cohortes d'apprenants.
    """

    def __init__(self, content_area):
        """Initialise la page avec les conteneurs d'affichage et de saisie."""
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_aav_ids = None
        self.champ_onto_id = None

    def _set_result(self, text: str, color: str = "#212121"):
        """Met a jour la zone de notification avec le texte et la couleur specifies."""
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        if self._page: self._page.update()

    def _fmt(self, res) -> str:
        """Formate dynamiquement les resultats JSON pour un rendu textuel structure."""
        if not res: return "Aucune donnee disponible."
        if isinstance(res, list):
            lines = []
            for i, item in enumerate(res):
                lines.append(f"Resultat #{i+1}")
                lines.append(self._fmt(item))
                lines.append("-" * 30)
            return "\n".join(lines)
        if isinstance(res, dict):
            lines = []
            for k, v in res.items():
                key_clean = str(k).replace("_", " ").capitalize()
                lines.append(f"{key_clean:25}: {v}")
            return "\n".join(lines)
        return str(res)

    def _handle_response(self, response: httpx.Response) -> bool:
        """Evalue la reponse HTTP et retourne un booleen de succes."""
        if response.status_code == 200: return True
        
        msg = f"Erreur de communication ({response.status_code})"
        if response.status_code == 404: msg = "Aucune donnee identifiee pour ces criteres."
        elif response.status_code == 400: msg = "Arguments de requete invalides."
        
        try:
            detail = response.json().get("detail")
            if detail: msg += f"\nNote technique : {detail}"
        except: pass
        
        self._set_result(msg, "#F44336")
        return False

    def comparer_aavs(self, e):
        """Execute une requete de comparaison entre plusieurs referentiels AAV."""
        ids = self.champ_aav_ids.value.strip()
        if not ids:
            self._set_result("Format requis : liste d'identifiants numeriques (ex: 1,2,3).", "#F57F17")
            return
        
        self._set_result("Interrogation du module analytique...")
        try:
            r = httpx.get(f"{BASE_URL}/metrics/compare/aavs", params={"ids": ids}, timeout=10)
            if self._handle_response(r):
                self._set_result(self._fmt(r.json()))
        except httpx.ConnectError:
            self._set_result("Serveur API distant injoignable.", "#F44336")
        except Exception as err:
            self._set_result(f"Exception detectee : {err}", "#F44336")

    def comparer_learners(self, e):
        """Execute une requete de comparaison des performances apprenants par ontologie."""
        onto_id = self.champ_onto_id.value.strip()
        if not onto_id:
            self._set_result("Veuillez saisir l'identifiant de l'ontologie cible.", "#F57F17")
            return
        
        self._set_result("Traitement de la comparaison cohortes...")
        try:
            r = httpx.get(f"{BASE_URL}/metrics/compare/learners", params={"id_ontologie": onto_id}, timeout=10)
            if self._handle_response(r):
                self._set_result(self._fmt(r.json()))
        except httpx.ConnectError:
            self._set_result("Serveur API distant injoignable.", "#F44336")
        except Exception as err:
            self._set_result(f"Exception detectee : {err}", "#F44336")

    def build(self, page: ft.Page):
        """Construit l'interface de comparaison avec les formulaires de recherche."""
        self._page = page
        cor_prim = "#6A1B9A"
        
        self.champ_aav_ids = ft.TextField(label="IDs Referentiels (ex: 1, 3, 5)", width=250, border_color=cor_prim)
        self.champ_onto_id = ft.TextField(label="ID Ontologie (ex: 1)", width=250, border_color=cor_prim)
        
        self.affichage_resultat = ft.Text("Systeme pret pour l'analyse.", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=700, height=400, bgcolor="#FFFFFF", border_radius=10, padding=16,
            border=ft.border.all(1, "#E1BEE7"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Analyse Comparative des Performances", size=28, weight="bold", color=cor_prim),
                ft.Text("Observation des ecarts de reussite entre ressources et apprenants.", size=14, color="#616161"),
                ft.Divider(height=20, color="transparent"),
                ft.Row([
                    ft.Column([
                        self.champ_aav_ids,
                        ft.ElevatedButton("Comparer AAV", icon=ft.Icons.COMPARE_ARROWS, on_click=self.comparer_aavs, bgcolor=cor_prim, color="white"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.VerticalDivider(width=40),
                    ft.Column([
                        self.champ_onto_id,
                        ft.ElevatedButton("Comparer Apprenants", icon=ft.Icons.PEOPLE, on_click=self.comparer_learners, bgcolor="#8E24AA", color="white"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=30, color="transparent"),
                boite_resultat,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            bgcolor="#FFFFFF", expand=True, padding=30
        )
