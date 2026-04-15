import sys
import httpx
import json
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class ActivitepedagogiquePage:
    """
    Page de gestion des activites pedagogiques.
    Permet de gerer le cycle de vie des activites (creation, demarrage, completion)
    et de consulter les exercices associes.
    """

    def __init__(self, content_area, is_professor=False):
        """Initialise la page avec les references de navigation et les droits d'acces."""
        self.content_area = content_area
        self.is_professor = is_professor
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None
        self.bouton_modifier = None
        self.bouton_supprimer = None

    def _set_result(self, text: str, color: str = "#212121"):
        """Met a jour la zone de texte centrale des resultats."""
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        if self._page:
            self._page.update()

    def _handle_response(self, response: httpx.Response, success_msg: str = None) -> bool:
        """Traite les reponses de l'API et affiche les informations structurees."""
        if response.status_code in [200, 201, 204]:
            if success_msg:
                self._set_result(success_msg, "#4CAF50")
            return True
        
        msg = f"Erreur {response.status_code}"
        if response.status_code == 404:
            msg = "Activite introuvable."
        elif response.status_code == 400:
            msg = "Donnees invalides."
            
        try:
            detail = response.json().get("detail")
            if detail: msg += f"\n({detail})"
        except: pass

        self._set_result(msg, "#F44336")
        return False

    def _fmt(self, res) -> str:
        """Formate les donnees (listes ou dictionnaires) pour un affichage textuel lisible."""
        if not res: return "Aucune donnee."
        if isinstance(res, list):
            lines = []
            for item in res:
                lines.append(self._fmt(item))
                lines.append("-" * 40)
            return "\n".join(lines)
        if isinstance(res, dict):
            lines = []
            for k, v in res.items():
                key_clean = str(k).replace("_", " ").title()
                lines.append(f"{key_clean:20}: {v}")
            return "\n".join(lines)
        return str(res)

    def rechercher(self, e=None):
        """Recherche une activite specifique par son identifiant unique."""
        if not self.champ_id.value: return
        try:
            r = httpx.get(f"{BASE_URL}/activites/{int(self.champ_id.value)}", timeout=5)
            if self._handle_response(r):
                self._set_result(self._fmt(r.json()))
                self.secure_set_visible(self.bouton_modifier, True)
                self.secure_set_visible(self.bouton_supprimer, True)
            else:
                self.secure_set_visible(self.bouton_modifier, False)
                self.secure_set_visible(self.bouton_supprimer, False)
        except Exception as err:
            self._set_result(f"Serveur inaccessible : {err}", "#F44336")
        self._page.update()

    def voir_liste(self, e):
        """Affiche le referentiel complet des activites dans une fenêtre modale."""
        try:
            r = httpx.get(BASE_URL + "/activites/", timeout=5)
            if not self._handle_response(r): return
            data = r.json()
            items_raw = data if isinstance(data, list) else data.get("items", [])

            def selectionner(id_v):
                self.champ_id.value = str(id_v)
                dialog.open = False
                self._page.update()
                self.rechercher()

            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.AUTO_STORIES, color="#F57F17"),
                    title=ft.Text(f"#{a.get('id', a.get('id_activite', '?'))} - {a.get('nom', '')}", weight="bold"),
                    subtitle=ft.Text(str(a.get("type_activite", ""))),
                    on_click=lambda e, id_v=a.get("id", a.get("id_activite")): selectionner(id_v),
                )
                for a in items_raw
            ]
            dialog = ft.AlertDialog(
                title=ft.Text("Referentiel des Activites"),
                content=ft.Container(content=ft.ListView(items, spacing=8, padding=10), width=500, height=500),
                actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())],
            )
            self._page.overlay.append(dialog)
            dialog.open = True
            self._page.update()
        except:
            self._set_result("Erreur lors du chargement de la liste.", "#F44336")

    def ouvrir_creation(self, e):
        """Ouvre un dialogue de creation pour une nouvelle activite pedagogique."""
        champ_nom = ft.TextField(label="Nom de l'activite", width=400)
        champ_type = ft.TextField(label="Typologie (ex: Pilotage)", width=400)
        champ_desc = ft.TextField(label="Description", width=400, multiline=True, min_lines=2)
        champ_disc = ft.TextField(label="Discipline", width=400)
        champ_level = ft.TextField(label="Difficulte", width=400)

        def valider(ev):
            try:
                body = {
                    "nom": champ_nom.value, "type_activite": champ_type.value,
                    "description": champ_desc.value, "discipline": champ_disc.value,
                    "niveau_difficulte": champ_level.value
                }
                r = httpx.post(BASE_URL + "/activites/", json=body, timeout=5)
                if self._handle_response(r, "Activite creee."):
                    res = r.json()
                    id_key = "id_activite" if "id_activite" in res else "id"
                    self.champ_id.value = str(res.get(id_key, ""))
                    dialog.open = False
                    self._page.update()
                    self.rechercher()
            except Exception as err:
                self._set_result(f"Echec creation : {err}", "#F44336")

        dialog = ft.AlertDialog(
            title=ft.Text("Nouvelle Activite"),
            content=ft.Column([champ_nom, champ_type, champ_desc, champ_disc, champ_level], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Creer", on_click=valider, bgcolor="#4CAF50", color="white"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_modifier(self, e):
        """Permet la modification des donnees d'une activite existante."""
        if not self.champ_id.value: return
        try:
            r = httpx.get(f"{BASE_URL}/activites/{int(self.champ_id.value)}", timeout=5)
            if not self._handle_response(r): return
            res = r.json()
        except: return

        champ_nom = ft.TextField(label="Nom", value=res.get("nom", ""), width=400)
        champ_type = ft.TextField(label="Type", value=res.get("type_activite", ""), width=400)
        champ_desc = ft.TextField(label="Description", value=res.get("description", ""), width=400, multiline=True, min_lines=2)
        champ_disc = ft.TextField(label="Discipline", value=res.get("discipline", ""), width=400)
        champ_level = ft.TextField(label="Difficulte", value=res.get("niveau_difficulte", ""), width=400)

        def sauvegarder(ev):
            try:
                body = {
                    "nom": champ_nom.value, "type_activite": champ_type.value,
                    "description": champ_desc.value, "discipline": champ_disc.value,
                    "niveau_difficulte": champ_level.value
                }
                r = httpx.put(BASE_URL + f"/activites/{self.champ_id.value}", json=body, timeout=5)
                if self._handle_response(r, "Modifications enregistrees."):
                    dialog.open = False
                    self._page.update()
                    self.rechercher()
            except Exception as err:
                self._set_result(f"Erreur : {err}", "#F44336")

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modification - Activite #{self.champ_id.value}"),
            content=ft.Column([champ_nom, champ_type, champ_desc, champ_disc, champ_level], scroll=ft.ScrollMode.AUTO, tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Sauvegarder", on_click=sauvegarder, color="white", bgcolor="#4CAF50"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def action_supprimer(self, e):
        """Demande confirmation avant la suppression definitive d'une activite."""
        if not self.champ_id.value: return

        def confirmer(ev):
            try:
                r = httpx.delete(BASE_URL + f"/activites/{self.champ_id.value}", timeout=5)
                if self._handle_response(r, "Activite supprimee."):
                    self.secure_set_visible(self.bouton_modifier, False)
                    self.secure_set_visible(self.bouton_supprimer, False)
                    self.champ_id.value = ""
            except:
                self._set_result("Echec de la suppression.", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmation de suppression"),
            content=ft.Text(f"Supprimer definitivement l'activite #{self.champ_id.value} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="white", bgcolor="#F44336"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def voir_exercices(self, e):
        """Recupere et affiche la liste des exercices lies a l'activite."""
        if not self.champ_id.value: return
        try:
            r = httpx.get(f"{BASE_URL}/activites/{int(self.champ_id.value)}/exercises", timeout=5)
            if self._handle_response(r):
                self._set_result(self._fmt(r.json()))
        except:
            self._set_result("Impossible de charger les exercices.", "#F44336")

    def demarrer(self, e):
        """Notifie le systeme du demarrage de l'activite par l'enseignant."""
        if not self.champ_id.value: return
        try:
            r = httpx.post(f"{BASE_URL}/activites/{int(self.champ_id.value)}/start", timeout=5)
            if self._handle_response(r, "Session demarree."):
                self._set_result(self._fmt(r.json()))
        except:
            self._set_result("Erreur demarrage.", "#F44336")

    def completer(self, e):
        """Cloture l'activite en cours et verifie sa completion."""
        if not self.champ_id.value: return
        try:
            r = httpx.post(f"{BASE_URL}/activites/{int(self.champ_id.value)}/complete", timeout=5)
            if self._handle_response(r, "Session cloturee."):
                self._set_result(self._fmt(r.json()))
        except:
            self._set_result("Erreur completion.", "#F44336")

    def build(self, page: ft.Page):
        """Genere l'interface visuelle de la page des activites."""
        self._page = page
        COLOR_PRIMARY = "#F57F17"

        self.champ_id = ft.TextField(
            label="ID Activite", width=200, keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10, border_color="#FFB300", bgcolor="#FFF8E1",
            prefix_icon=ft.Icons.SEARCH
        )
        self.affichage_resultat = ft.Text("Pret.", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton("Modifier", visible=False, on_click=self.ouvrir_modifier, color="white", bgcolor="#F9A825")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="white", bgcolor="#F44336")

        def secure_set_visible(btn, val):
            btn.visible = val if self.is_professor else False
        self.secure_set_visible = secure_set_visible

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380, bgcolor="#FFFFFF", border_radius=10, padding=16,
            border=ft.border.all(1, "#FFE082"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK))
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Activites Pedagogiques", size=28, weight="bold", color=COLOR_PRIMARY),
                self.champ_id,
                ft.Row([
                    ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.rechercher, bgcolor=COLOR_PRIMARY, color="white"),
                    ft.ElevatedButton("Referentiel", icon=ft.Icons.LIST, on_click=self.voir_liste, bgcolor="#F9A825", color="white"),
                    ft.ElevatedButton("Nouveau", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor="#43A047", color="white", visible=self.is_professor),
                ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                ft.Row([
                    ft.ElevatedButton("Lier Exercices", icon=ft.Icons.FITNESS_CENTER, on_click=self.voir_exercices, bgcolor="#0288D1", color="white"),
                    ft.ElevatedButton("Demarrer", icon=ft.Icons.PLAY_ARROW, on_click=self.demarrer, bgcolor="#43A047", color="white", visible=self.is_professor),
                    ft.ElevatedButton("Cloturer", icon=ft.Icons.CHECK_CIRCLE, on_click=self.completer, bgcolor="#2E7D32", color="white", visible=self.is_professor),
                ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                boite_resultat,
                ft.Row([self.bouton_modifier, self.bouton_supprimer], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=20, expand=True
        )
