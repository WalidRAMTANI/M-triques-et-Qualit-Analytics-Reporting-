import sys
import requests
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class SessionsPage:
    """
    Classe pour la gestion du cycle de vie des sessions d'apprentissage.
    Permet de creer, demarrer, cloturer et supprimer des sessions via l'API.
    """

    def __init__(self, content_area, is_professor=False):
        """Initialise la page avec les delegues de navigation et les etats de role."""
        self.content_area = content_area
        self.is_professor = is_professor
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_demarrer = None
        self.bouton_cloturer = None
        self.bouton_supprimer = None

    def _set_result(self, text: str, color: str = "#212121"):
        """Met a jour la zone de texte affichant les resultats des operations."""
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def rechercher(self, e=None):
        """Recherche les details d'une session specifique par son identifiant."""
        if not self.champ_id.value:
            return
        try:
            response = requests.get(f"http://127.0.0.1:8000/sessions/{int(self.champ_id.value)}")
            if response.status_code == 200:
                res = response.json()
                self._set_result(
                    f"Session ID : {res.get('id_session')}\n"
                    f"ID Activite : {res.get('id_activite')}\n"
                    f"ID Apprenant : {res.get('id_apprenant')}\n"
                    f"Statut : {str(res.get('statut', '')).upper()}\n"
                    f"Debut : {res.get('date_debut')}\n"
                    f"Fin : {res.get('date_fin')}\n"
                    f"Bilan : {res.get('bilan')}\n"
                )
                self.secure_set_visible(self.bouton_demarrer, True)
                self.secure_set_visible(self.bouton_cloturer, True)
                self.secure_set_visible(self.bouton_supprimer, True)
            elif response.status_code == 404:
                self._set_result("Session introuvable.", "#F44336")
                self.bouton_demarrer.visible = False
                self.bouton_cloturer.visible = False
                self.bouton_supprimer.visible = False
            else:
                self._set_result(f"Erreur de recherche (Code {response.status_code})", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur technique : {err}", "#F44336")
        finally:
            self._page.update()

    def ouvrir_liste(self, e):
        """Affiche la liste complete des sessions dans un dialogue modal."""
        try:
            response = requests.get("http://127.0.0.1:8000/sessions/")
            if response.status_code == 200:
                res = response.json()
                liste = res.get("sessions", []) if isinstance(res, dict) else res
            else:
                return
        except:
            return

        def charger(id_s):
            self.champ_id.value = str(id_s)
            dialog.open = False
            self._page.update()
            self.rechercher()

        items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color="#7B1FA2"),
                title=ft.Text(f"Session {s['id_session']}", weight="bold"),
                subtitle=ft.Text(f"Statut: {s['statut']}"),
                on_click=lambda e, id_v=s["id_session"]: charger(id_v),
            )
            for s in liste
        ]
        dialog = ft.AlertDialog(
            title=ft.Text("Liste des Sessions"),
            content=ft.Container(content=ft.ListView(items, spacing=10), width=500, height=500),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_creation(self, e):
        """Ouvre un formulaire modal pour creer une nouvelle session d'apprentissage."""
        champ_activite = ft.TextField(label="ID Activite", keyboard_type=ft.KeyboardType.NUMBER)
        champ_apprenant = ft.TextField(label="ID Apprenant", keyboard_type=ft.KeyboardType.NUMBER)

        def valider(ev):
            try:
                donnees = {"id_activite": int(champ_activite.value), "id_apprenant": int(champ_apprenant.value)}
                response = requests.post("http://127.0.0.1:8000/sessions/", json=donnees)
                if response.status_code in [200, 201]:
                    res = response.json()
                    dialog.open = False
                    self.champ_id.value = str(res.get("id_session", ""))
                    self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur de creation : {err}", "#F44336")

        dialog = ft.AlertDialog(
            title=ft.Text("Nouvelle Session"),
            content=ft.Column([champ_activite, champ_apprenant], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Creer", on_click=valider, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def demarrer(self, e):
        """Envoie une requête pour marquer la session comme active."""
        if not self.champ_id.value: return
        try:
            response = requests.put(f"http://127.0.0.1:8000/sessions/{int(self.champ_id.value)}/start")
            if response.status_code == 200:
                self._set_result("Session demarree avec succes.", "#4CAF50")
                self.rechercher()
        except Exception as err:
            self._set_result(f"Erreur de demarrage : {err}", "#F44336")

    def cloturer(self, e):
        """Envoie une requête pour fermer la session et generer un bilan automatique."""
        if not self.champ_id.value: return
        try:
            response = requests.put(f"http://127.0.0.1:8000/sessions/{int(self.champ_id.value)}/close")
            if response.status_code == 200:
                res = response.json()
                bilan = res.get("summary", {})
                self._set_result(
                    f"Session cloturee\n"
                    f"Tentatives : {bilan.get('total_attempts')}\n"
                    f"Reussites : {bilan.get('valid_attempts')}\n"
                    f"Score moyen : {float(bilan.get('average_score', 0)):.2f}\n",
                    "#4CAF50",
                )
            else:
                self._set_result(f"Erreur lors de la cloture: {response.status_code}", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur technique de cloture : {err}", "#F44336")

    def action_supprimer(self, e):
        """Action de suppression d'une session avec confirmation modale."""
        def confirmer(ev):
            try:
                response = requests.delete(f"http://127.0.0.1:8000/sessions/{int(self.champ_id.value)}")
                if response.status_code in [200, 204]:
                    self._set_result("Session supprimee.", "#4CAF50")
                    self.secure_set_visible(self.bouton_demarrer, False)
                    self.secure_set_visible(self.bouton_cloturer, False)
                    self.secure_set_visible(self.bouton_supprimer, False)
                    self.champ_id.value = ""
            except Exception as err:
                self._set_result(f"Erreur de suppression : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Supprimer la session ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Confirmer", on_click=confirmer, color="#FFFFFF", bgcolor="#F44336"),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def build(self, page: ft.Page):
        """Construction de l'interface utilisateur de la page."""
        self._page = page
        COLOR_PRIMARY = "#7B1FA2"

        self.champ_id = ft.TextField(
            label="ID Session", width=200, border_radius=10,
            border_color="#9C27B0", bgcolor="#F3E5F5", prefix_icon=ft.Icons.SEARCH
        )
        self.affichage_resultat = ft.Text("En attente de recherche.", size=14)
        
        self.bouton_demarrer = ft.ElevatedButton("Demarrer", visible=False, on_click=self.demarrer, bgcolor="#42A5F5", color="white")
        self.bouton_cloturer = ft.ElevatedButton("Cloturer", visible=False, on_click=self.cloturer, bgcolor="#FFA000", color="white")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, bgcolor="#EF5350", color="white")

        def secure_set_visible(btn, val):
            btn.visible = val if self.is_professor else False
        self.secure_set_visible = secure_set_visible

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380, bgcolor="#FFFFFF", border_radius=10, padding=16,
            border=ft.border.all(1, "#E1BEE7")
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Suivi des Sessions d'Apprenant", size=28, weight="bold", color=COLOR_PRIMARY),
                self.champ_id,
                ft.Row([
                    ft.ElevatedButton("Chercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color="white"),
                    ft.ElevatedButton("Nouvelle", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor="#66BB6A", color="white", visible=self.is_professor),
                    ft.ElevatedButton("Toutes", icon=ft.Icons.LIST, on_click=self.ouvrir_liste, bgcolor="#AB47BC", color="white"),
                ], alignment=ft.MainAxisAlignment.CENTER),
                boite_resultat,
                ft.Row([self.bouton_demarrer, self.bouton_cloturer, self.bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            padding=20, expand=True
        )
