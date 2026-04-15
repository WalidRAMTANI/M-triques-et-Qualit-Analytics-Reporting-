import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import requests
import flet as ft
from pydantic import ValidationError
from app.model.model import LearnerCreate, LearnerUpdate, TentativeCreate

class LearnersPage:
    """
    Page de gestion des profils apprenants.
    Permet le suivi individuel, l'analyse de progression et la simulation d'activites pedagogiques.
    """

    def __init__(self, content_area, is_professor=False):
        """Initialise la page avec les composants de recherche et les permissions."""
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
        """Gere les retours de l'API et affiche les notifications de status."""
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
            msg = "Profil introuvable."
        elif response.status_code == 400:
            msg = "Donnees incorrectes."
            
        try:
            detail = response.json().get("detail")
            if detail: msg += f" - {detail}"
        except: pass

        self._set_error(msg)
        return False

    def _format_value(self, v):
        """Formate dynamiquement les types complexes pour un rendu visuel propre."""
        if v is None:
            return "---"
        if isinstance(v, list):
            if not v:
                return "Aucune donnee."
            return ", ".join(str(i) for i in v)
        if isinstance(v, dict):
            if not v:
                return "Aucune information."
            res = ""
            for sub_k, sub_v in v.items():
                res += f"* {str(sub_k).capitalize()}: {self._format_value(sub_v)}\n"
            return res.strip()
        return str(v)

    def _dict_to_ui(self, data: dict, title="Fiche Apprenant"):
        """Genere l'interface utilisateur pour afficher les details d'un apprenant."""
        rows = []
        for k, v in data.items():
            k_clean = str(k).replace("_", " ").title()
            val_str = self._format_value(v)
            rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"{k_clean}", weight="w600", color="#3949AB", size=14, width=170),
                        ft.Text(val_str, color="#424242", size=14, expand=True, selectable=True)
                    ], vertical_alignment=ft.CrossAxisAlignment.START),
                    padding=ft.padding.symmetric(vertical=12, horizontal=8),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, "#EEEEEE"))
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ASSIGNMENT_IND, color="#1A237E", size=24),
                    ft.Text(title, size=20, weight="bold", color="#1A237E"),
                ]),
                ft.Divider(color="#E8EAF6", height=20),
                *rows
            ], scroll=ft.ScrollMode.AUTO),
            padding=24, bgcolor="#FFFFFF", border_radius=16
        )

    def rechercher(self, e=None):
        """Effectue une requete pour recuperer les informations d'un apprenant par son ID."""
        if getattr(self.champ_id, "value", None) is None:
            self._set_error("Veuillez selectionner un apprenant.")
            return
        
        self._set_result_content(ft.ProgressRing(color="#3949AB"))
        try:
            response = requests.get(f"http://127.0.0.1:8000/learners/{int(self.champ_id.value)}")
            if self._handle_response(response):
                data = response.json()
                apprenant_name = data.get("nom_utilisateur", f"Apprenant #{self.champ_id.value}")
                self._set_result_content(self._dict_to_ui(data, title=f"Fiche de {apprenant_name}"))
                self.secure_set_visible(self.bouton_modifier, True)
                self.secure_set_visible(self.bouton_supprimer, True)
            else:
                self.secure_set_visible(self.bouton_modifier, False)
                self.secure_set_visible(self.bouton_supprimer, False)
        except Exception as err:
            self._set_error(f"Erreur technique : {err}")

    def ouvrir_liste(self, e):
        """Affiche la liste exhaustive des apprenants dans un dialogue modal."""
        self._set_result_content(ft.ProgressRing(color="#3949AB"))
        try:
            response = requests.get("http://127.0.0.1:8000/learners/")
            if not self._handle_response(response): return
            data = response.json()
        except:
            self._set_error("Serveur inaccessible.")
            return
            
        items_raw = data if isinstance(data, list) else data.get("learners", [])

        def selectionner(id_v):
            self.champ_id.value = str(id_v)
            dialog.open = False
            self._page.update()
            self.rechercher()

        cards = []
        for l in items_raw:
            id_val = l.get('id_apprenant', l.get('id', '?'))
            name = l.get('nom_utilisateur', f"Etudiant #{id_val}")
            
            cards.append(ft.Container(
                content=ft.ListTile(
                    leading=ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON), bgcolor="#E8EAF6", color="#3949AB"),
                    title=ft.Text(name, weight="bold"),
                    subtitle=ft.Text(f"ID : {id_val}"),
                    on_click=lambda e, idx=id_val: selectionner(idx),
                ),
                border_radius=8, bgcolor="#FAFAFA"
            ))

        dialog = ft.AlertDialog(
            title=ft.Text("Referentiel des Apprenants"),
            content=ft.Container(content=ft.ListView(cards, padding=10), width=450, height=450),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_creation(self, e):
        """
        Affiche le formulaire de creation pour un nouveau profil etudiant.
        Valide les donnees via Pydantic (LearnerCreate) avant l'envoi API.
        """
        champ_nom = ft.TextField(label="Nom Complet", width=350)
        champ_email = ft.TextField(label="Adresse Email", width=350)
        err_text = ft.Text("", color="red", visible=False)

        def valider(ev):
            try:
                learner_data = LearnerCreate(
                    nom_utilisateur=champ_nom.value or "",
                    email=champ_email.value or ""
                )
                response = requests.post("http://127.0.0.1:8000/learners/", json=learner_data.model_dump())
                if self._handle_response(response, "Profil cree avec succes."):
                    res = response.json()
                    dialog.open = False
                    self.champ_id.value = str(res.get("id_apprenant", res.get("id", "")))
                    self._page.update()
                    self.rechercher()
            except ValidationError as ve:
                err_text.value = f"Erreur de format : {ve.errors()[0]['msg']}"
                err_text.visible = True
                self._page.update()
            except Exception as err:
                self._set_error(f"Erreur technique : {err}")

        dialog = ft.AlertDialog(
            title=ft.Text("Nouveau Profil"),
            content=ft.Column([err_text, champ_nom, champ_email], tight=True, spacing=15),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Enregistrer", on_click=valider, bgcolor="#4CAF50", color="white"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def ouvrir_modifier(self, e):
        """
        Affiche le formulaire de modification d'un profil apprenant existant.

        Valide les donnees via Pydantic (LearnerUpdate) avant d'effectuer
        la requete PUT. Seuls les champs renseignes sont envoyes.
        """
        if not getattr(self.champ_id, "value", None):
            return
        champ_nom = ft.TextField(label="Nom de l'utilisateur", width=350)
        champ_email = ft.TextField(label="Contact Email", width=350)
        err_text = ft.Text("", color="red", visible=False)

        def sauvegarder(ev):
            try:
                update_data = LearnerUpdate(
                    nom_utilisateur=champ_nom.value or None,
                    email=champ_email.value or None
                )
                payload = update_data.model_dump(exclude_none=True)
                if not payload:
                    err_text.value = "Veuillez renseigner au moins un champ."
                    err_text.visible = True
                    self._page.update()
                    return
                response = requests.put(f"http://127.0.0.1:8000/learners/{int(self.champ_id.value)}", json=payload)
                if self._handle_response(response, "Profil actualise."):
                    self.rechercher()
            except ValidationError as ve:
                err_text.value = f"Donnee invalide : {ve.errors()[0]['msg']}"
                err_text.visible = True
                self._page.update()
                return
            except Exception as err:
                self._set_error(f"Erreur : {err}")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Modification de compte"),
            content=ft.Column([err_text, champ_nom, champ_email], tight=True, spacing=15),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Appliquer", on_click=sauvegarder, color="white", bgcolor="#FF9800"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def action_supprimer(self, e):
        """Demande confirmation puis supprime le profil de la base de donnees."""
        if not self.champ_id.value: return
        def confirmer(ev):
            try:
                response = requests.delete(f"http://127.0.0.1:8000/learners/{int(self.champ_id.value)}")
                if self._handle_response(response, "Compte supprime."):
                    self.secure_set_visible(self.bouton_modifier, False)
                    self.secure_set_visible(self.bouton_supprimer, False)
                    self.champ_id.value = ""
            except:
                self._set_error("Echec de la suppression.")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Suppression Definitive"),
            content=ft.Text("Voulez-vous supprimer ce profil ? Cette action est irreversible."),
            actions=[
                ft.TextButton("Abandonner", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="white", bgcolor="#F44336"),
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def voir_progression(self, e):
        """Affiche l'etat actuel de maitrise des AAV pour l'apprenant selectionne."""
        if not self.champ_id.value: 
            self._set_error("ID requis.")
            return
        self._set_result_content(ft.ProgressRing(color="#3949AB"))
        try:
            response = requests.get(f"http://127.0.0.1:8000/learners/{int(self.champ_id.value)}/progress")
            if self._handle_response(response):
                self._set_result_content(self._dict_to_ui(response.json(), title="Maitrise des AAV"))
        except Exception as err:
            self._set_error(f"Erreur technique : {err}")

    def voir_statuts(self, e):
        """Recupere les statuts d'apprentissage detailles via l'API."""
        if not self.champ_id.value: return
        self._set_result_content(ft.ProgressRing(color="#3949AB"))
        try:
            response = requests.get(f"http://127.0.0.1:8000/learners/{int(self.champ_id.value)}/learning-status")
            if self._handle_response(response):
                self._set_result_content(self._dict_to_ui(response.json(), title="Statuts d'Apprentissage"))
        except:
            self._set_error("Impossible de recuperer les statuts.")

    def ouvrir_simulation_tentative(self, e):
        """
        Lance l'interface de simulation Pydantic pour generer des tentatives fictives.
        Valide avec TentativeCreate avant soumission de l'exercice au Backend API.
        """
        if not getattr(self.champ_id, "value", None):
            self._set_error("Veuillez selectionner un apprenant.")
            return

        champ_aav = ft.TextField(label="Cible AAV (ID)", keyboard_type=ft.KeyboardType.NUMBER)
        champ_score = ft.Slider(min=0, max=100, divisions=10, label="{value}%", value=80)
        err_text = ft.Text("", color="red", visible=False)
        
        def valider(ev):
            try:
                tentative_data = TentativeCreate(
                    id_apprenant=int(self.champ_id.value),
                    id_aav_cible=int(champ_aav.value),
                    score_obtenu=float(champ_score.value / 100.0),
                    id_exercice_ou_evenement=1,
                    est_valide=True,
                    temps_resolution_secondes=45
                )
                response = requests.post("http://127.0.0.1:8000/attempts/", json=tentative_data.model_dump())
                if self._handle_response(response, "Tentative enregistree."):
                    dialog.open = False
                    self.voir_progression(None)
                else:
                    err_text.value = f"Refus API: {response.text}"
                    err_text.visible = True
                    self._page.update()
            except ValidationError as ve:
                err_text.value = f"Saisie invalide (Pydantic) : {ve.errors()[0]['msg']}"
                err_text.visible = True
                self._page.update()
            except ValueError:
                err_text.value = "Identifiant d'AAV invalide (doit etre numerique)."
                err_text.visible = True
                self._page.update()
            except Exception as ex:
                err_text.value = f"Echec de la simulation : {ex}"
                err_text.visible = True
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Simulation Pedagogique"),
            content=ft.Column([err_text, champ_aav, ft.Text("Niveau de performance :"), champ_score], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Simuler", on_click=valider, bgcolor="#FF6F00", color="white")
            ]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def build(self, page: ft.Page):
        """Cree la structure visuelle de la page de gestion des apprenants."""
        self._page = page
        
        # Charger les apprenants pour le Dropdown
        self.champ_id = ft.Dropdown(
            label="Selection Apprenant", width=250, border_radius=12,
            bgcolor="#FFFFFF"
        )
        try:
            resp = requests.get("http://127.0.0.1:8000/learners/")
            if resp.status_code == 200:
                data = resp.json()
                items = data if isinstance(data, list) else data.get("learners", [])
                opts = []
                for l in items:
                    id_val = l.get("id_apprenant", l.get("id"))
                    opts.append(ft.dropdown.Option(str(id_val), f"#{id_val} - {l.get('nom_utilisateur')}"))
                self.champ_id.options = opts
        except Exception:
            pass
        
        self.result_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=60, color="#B0BEC5"),
                ft.Text("Entrez un identifiant ou parcourez la liste.", color="#90A4AE")
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=800, height=450, bgcolor="#FAFAFC", border_radius=16, 
            padding=20, border=ft.border.all(1, "#E8EAF6")
        )
        
        self.bouton_modifier = ft.ElevatedButton("Modifier Profil", icon=ft.Icons.EDIT, visible=False, on_click=self.ouvrir_modifier, bgcolor="#FFB300", color="white")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer Profil", icon=ft.Icons.DELETE, visible=False, on_click=self.action_supprimer, bgcolor="#E53935", color="white")

        def secure_set_visible(btn, val):
            btn.visible = val if self.is_professor else False
        self.secure_set_visible = secure_set_visible

        def _action_btn(icon, text, click_handler, color, bg):
            return ft.ElevatedButton(text, icon=icon, on_click=click_handler, color=color, bgcolor=bg, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))

        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PEOPLE_ALT, size=40, color="#283593"),
                ft.Text("Referentiel Apprenants", size=28, weight="bold", color="#283593"),
            ]), margin=ft.margin.only(bottom=20)
        )

        controls = ft.Row([
            self.champ_id,
            _action_btn(ft.Icons.SEARCH, "Chercher", self.rechercher, "white", "#283593"),
            _action_btn(ft.Icons.LIST, "Liste", self.ouvrir_liste, "white", "#3F51B5"),
            _action_btn(ft.Icons.PERSON_ADD, "Nouveau", self.ouvrir_creation, "white", "#43A047") if self.is_professor else ft.Container(),
        ], wrap=True)
        
        analytics = ft.Row([
            _action_btn(ft.Icons.AUTO_GRAPH, "Maitrise Generale", self.voir_progression, "white", "#00ACC1"),
            _action_btn(ft.Icons.SCIENCE, "Simuler Tentative", self.ouvrir_simulation_tentative, "white", "#FF6F00"),
            _action_btn(ft.Icons.FACT_CHECK, "Statuts Detaillees", self.voir_statuts, "white", "#8E24AA"),
        ], spacing=15)

        return ft.Container(
            content=ft.Column([
                header,
                ft.Container(content=ft.Column([controls, analytics], spacing=20), bgcolor="#FFFFFF", padding=24, border_radius=16),
                self.result_container,
                ft.Row([self.bouton_modifier, self.bouton_supprimer], alignment=ft.MainAxisAlignment.END, spacing=15)
            ], scroll=ft.ScrollMode.AUTO),
            padding=40, expand=True, bgcolor="#F5F7FA"
        )
