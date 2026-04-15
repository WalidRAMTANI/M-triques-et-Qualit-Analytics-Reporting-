import sys
import flet as ft
import requests
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class AttemptsPage:
    """
    Page de gestion des tentatives d'exercices.
    Fournit des outils pour la creation, la recherche, la suppression et le traitement analytique des performances.
    """

    def __init__(self, content_area, is_professor=False):
        """Initialise la page avec les composants de recherche et de visualisation."""
        self.content_area = content_area
        self.is_professor = is_professor
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_supprimer = None
        self.bouton_traiter = None

    def _set_result(self, text: str, color: str = "#212121"):
        """Met a jour l'affichage des resultats avec une couleur specifique."""
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        if self._page: self._page.update()

    def _handle_response(self, response: requests.Response, success_msg: str = None) -> bool:
        """Centralise la gestion des codes HTTP et affiche les erreurs correspondantes."""
        if response.status_code in [200, 201, 204]:
            if success_msg: self._set_result(success_msg, "#4CAF50")
            return True
        
        msg = f"Erreur de communication ({response.status_code})."
        if response.status_code == 404: msg = "Tentative introuvable."
        elif response.status_code == 400: msg = "Donnees de requete invalides."
        elif response.status_code == 500: msg = "Incident technique serveur."
        
        try:
            detail = response.json().get("detail")
            if detail: msg += f"\nNote: {detail}"
        except: pass

        self._set_result(msg, "#F44336")
        return False

    def _fmt(self, res: dict) -> str:
        """Formate les donnees JSON en texte lisible pour l'interface."""
        return "\n".join([f"{k:25}: {v}" for k, v in res.items()])

    def rechercher(self, e=None):
        """Recherche une tentative specifique via son identifiant numerique."""
        if not self.champ_id.value: return
        try:
            response = requests.get(f"http://127.0.0.1:8000/attempts/{int(self.champ_id.value)}")
            if self._handle_response(response):
                self._set_result(self._fmt(response.json()))
                if self.is_professor:
                    self.bouton_supprimer.visible = True
                    self.bouton_traiter.visible = True
            else:
                self.bouton_supprimer.visible = False
                self.bouton_traiter.visible = False
        except requests.exceptions.ConnectionError:
            self._set_result("Serveur distant inaccessible.", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur d'execution : {err}", "#F44336")
        finally:
            if self._page: self._page.update()

    def ouvrir_liste(self, e):
        """Ouvre un dialogue listant l'ensemble des tentatives recensées."""
        try:
            response = requests.get("http://127.0.0.1:8000/attempts/")
            if not self._handle_response(response): return
            res_list = response.json()
        except:
            self._set_result("Erreur lors de la recuperation de la liste.", "#F44336")
            return

        items_raw = res_list if isinstance(res_list, list) else res_list.get("attempts", [])

        def selectionner(id_v):
            self.champ_id.value = str(id_v)
            dialog.open = False
            self._page.update()
            self.rechercher()

        items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.ASSIGNMENT, color="#E65100"),
                title=ft.Text(f"Tentative #{t.get('id', '?')}", weight="bold"),
                subtitle=ft.Text(f"Score: {t.get('score_obtenu', 'N/A')} | Valide: {t.get('est_valide', 'N/A')}"),
                on_click=lambda e, id_v=t.get("id"): selectionner(id_v),
            )
            for t in items_raw
        ]
        dialog = ft.AlertDialog(
            title=ft.Text("Historique des Tentatives"),
            content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
        )
        self._page.overlay.append(dialog); dialog.open = True; self._page.update()

    def ouvrir_creation(self, e):
        """Affiche un formulaire pour enregistrer une nouvelle tentative apprenant."""
        champ_apprenant = ft.TextField(label="ID Apprenant", width=250)
        champ_aav = ft.TextField(label="ID AAV Cible", width=250)
        champ_exercice = ft.TextField(label="ID Exercice", width=250)
        champ_score = ft.TextField(label="Score (0.0 a 1.0)", width=250, value="1.0")
        switch_valide = ft.Switch(label="Tentative valide", value=True)

        def valider(ev):
            try:
                donnees = {
                    "id_apprenant": int(champ_apprenant.value), "id_aav_cible": int(champ_aav.value),
                    "id_exercice_ou_evenement": int(champ_exercice.value),
                    "score_obtenu": float(champ_score.value), "est_valide": switch_valide.value
                }
                response = requests.post("http://127.0.0.1:8000/attempts/", json=donnees)
                if self._handle_response(response, "Nouvelle tentative enregistree."):
                    res = response.json()
                    self.champ_id.value = str(res.get("id", ""))
                    self.rechercher()
            except Exception as err:
                self._set_result(f"Donnees invalides : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Enregistrer une performance"),
            content=ft.Column([champ_apprenant, champ_aav, champ_exercice, champ_score, switch_valide], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Enregistrer", on_click=valider, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
            ],
        )
        self._page.overlay.append(dialog); dialog.open = True; self._page.update()

    def traiter(self, e):
        """Declenche le traitement algorithmique de la tentative pour mise a jour des acquis."""
        if not self.champ_id.value: return
        try:
            response = requests.post(f"http://127.0.0.1:8000/attempts/{int(self.champ_id.value)}/process")
            if self._handle_response(response, "Traitement analytique effectue."):
                res = response.json()
                self._set_result(f"Rapport de traitement :\n{self._fmt(res) if isinstance(res, dict) else str(res)}", "#4CAF50")
        except Exception as err:
            self._set_result(f"Echec du traitement : {err}", "#F44336")
        finally:
            self._page.update()

    def action_supprimer(self, e):
        """Demande confirmation puis supprime definitivement la tentative selectionnee."""
        if not self.champ_id.value: return

        def confirmer(ev):
            try:
                response = requests.delete(f"http://127.0.0.1:8000/attempts/{int(self.champ_id.value)}")
                if self._handle_response(response, "Tentative supprimee definitivement."):
                    self.bouton_supprimer.visible = False
                    self.bouton_traiter.visible = False
            except:
                self._set_result("Echec de la suppression.", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmation de suppression"),
            content=ft.Text(f"Voulez-vous supprimer la tentative #{self.champ_id.value} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Confirmer", on_click=confirmer, color="#FFFFFF", bgcolor="#F44336"),
            ],
        )
        self._page.overlay.append(dialog); dialog.open = True; self._page.update()

    def build(self, page: ft.Page):
        """Construit l'interface graphique de gestion des tentatives."""
        self._page = page
        cor_prim, cor_sec = "#E65100", "#FF5722"

        self.champ_id = ft.TextField(
            label="Identifiant Tentative", width=200, keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10, border_color=cor_sec, bgcolor="#FBE9E7",
            prefix_icon=ft.Icons.SEARCH, cursor_color=cor_prim
        )
        self.affichage_resultat = ft.Text("Resultat de la requete", size=14, color="#212121")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="#FFFFFF", bgcolor="#F44336")
        self.bouton_traiter = ft.ElevatedButton("Executer Traitement", visible=False, on_click=self.traiter, color="#FFFFFF", bgcolor="#FF9800")
        
        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380, bgcolor="#FFFFFF", border_radius=10, padding=16,
            border=ft.border.all(1, "#FFCCBC"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK))
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Historique des Tentatives d'Exercices", size=28, weight="bold", color=cor_prim),
                ft.Divider(height=20, color="transparent"),
                self.champ_id,
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=cor_prim, color="white"),
                    ft.ElevatedButton("Historique Global", icon=ft.Icons.LIST, on_click=self.ouvrir_liste, bgcolor=cor_sec, color="white"),
                    ft.ElevatedButton("Saisir Performance", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor="#43A047", color="white", visible=self.is_professor),
                ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                ft.Divider(height=15, color="transparent"),
                boite_resultat,
                ft.Divider(height=15, color="transparent"),
                ft.Row([self.bouton_traiter, self.bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, scroll=ft.ScrollMode.AUTO),
            bgcolor="#FFFFFF", expand=True, padding=20
        )
