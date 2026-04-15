import sys
import httpx
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://localhost:8000"

def _get(path: str):
    """Effectue une requete GET securisee vers l'API."""
    try:
        return httpx.get(f"{BASE_URL}{path}", timeout=5)
    except Exception as e:
        print(f"Erreur GET {path}: {e}")
        return None

def _put(path: str, payload: dict):
    """Effectue une requete PUT pour la mise a jour de donnees."""
    try:
        return httpx.put(f"{BASE_URL}{path}", json=payload, timeout=10)
    except Exception as e:
        print(f"Erreur PUT {path}: {e}")
        return None

def _delete(path: str):
    """Effectue une requete DELETE pour la suppression d'une ressource."""
    try:
        return httpx.delete(f"{BASE_URL}{path}", timeout=5)
    except Exception as e:
        print(f"Erreur DELETE {path}: {e}")
        return None

class DetailsPage:
    """
    Vue detaillee d'un Acquis d'Apprentissage Vise (AAV).
    Permet la consultation technique, la modification, la suppression et la generation de graphes.
    """

    def __init__(self, content_area, show_about_callback):
        """Initialise la page avec les references de navigation et les composants UI."""
        self.content_area = content_area
        self.show_about = show_about_callback
        self.page_content = None
        self.page = None
        self.aav_id = None
        self.affichage_resultat = None
        self.bouton_modifier = None
        self.bouton_supprimer = None
        self.markdown_display = None
        self.graph_display = None
        self.graph_image = None
        self.bouton_graph = None
        self.bouton_graph_interactif = None

    def build(self, aav_id, page):
        """Construit l'interface graphique complete pour l'AAV specifie."""
        self.page = page
        self.aav_id = aav_id

        self.affichage_resultat = ft.Text("Chargement des donnees...", size=14, color="#212121")
        self.bouton_modifier = ft.ElevatedButton("Modifier", visible=False, on_click=self.ouvrir_popup_modifier, color="white", bgcolor="#2196F3")
        self.bouton_supprimer = ft.ElevatedButton("Supprimer", visible=False, on_click=self.action_supprimer, color="white", bgcolor="#F44336")
        self.bouton_graph = ft.ElevatedButton("Graphe Statique", icon=ft.Icons.ACCOUNT_TREE, visible=False, on_click=self.afficher_graphe, color="white", bgcolor="#4CAF50")
        self.bouton_graph_interactif = ft.ElevatedButton("Graphe Interactif", icon=ft.Icons.WEB, visible=False, on_click=self.afficher_graphe_interactif, color="white", bgcolor="#9C27B0")

        self.markdown_display = ft.Markdown("", selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB)
        self.graph_image = ft.Image(src_base64="", visible=False, border_radius=10)
        self.graph_display = ft.Container(content=self.graph_image, visible=False, alignment=ft.alignment.center, padding=10, border=ft.border.all(1, "#E0E0E0"), border_radius=10)

        boite_resultat = ft.Container(
            content=ft.Column([
                self.affichage_resultat,
                ft.Divider(height=10),
                ft.Text("Description Technique :", weight="bold", size=16),
                ft.Container(content=self.markdown_display, padding=10, bgcolor="#F9F9F9", border_radius=5),
                ft.Divider(height=10),
                self.graph_display
            ], scroll=ft.ScrollMode.AUTO),
            width=750, height=500, bgcolor="#FFFFFF", border_radius=10, padding=16,
            shadow=ft.BoxShadow(blur_radius=10, color="#D0D0D0")
        )

        self.charger_aav(aav_id, boite_resultat)

        header = ft.Row([
            ft.Text(f"Fiche Technique AAV #{aav_id}", size=28, weight="bold", color="#1565C0", expand=True),
            ft.ElevatedButton("Retour", on_click=self.show_about, color="white", bgcolor="#1565C0"),
        ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.page_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20, color="transparent"),
                boite_resultat,
                ft.Divider(height=15, color="transparent"),
                ft.Row([self.bouton_modifier, self.bouton_supprimer, self.bouton_graph, self.bouton_graph_interactif], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, scroll=ft.ScrollMode.AUTO),
            bgcolor="#F5F5F5", expand=True, padding=20
        )
        return self.page_content

    def charger_aav(self, aav_id, boite_resultat):
        """Recupere les metadonnees de l'AAV et met a jour les composants visuels."""
        response = _get(f"/aavs/{aav_id}")

        if response and response.status_code == 200:
            res = response.json()
            prerequis_ids = res.get('prerequis_ids') or []
            prerequis_ids_str = ", ".join(map(str, prerequis_ids)) if prerequis_ids else "Aucun"
            prerequis_externes = res.get('prerequis_externes_codes') or []
            prerequis_externes_str = ", ".join(prerequis_externes) if prerequis_externes else "Aucun"

            details_text = (
                f"ID AAV: {res.get('id_aav', 'N/A')}\n"
                f"Nom: {res.get('nom', 'N/A')}\n"
                f"Discipline: {res.get('discipline', 'N/A')}\n"
                f"Enseignement: {res.get('enseignement', 'N/A')}\n"
                f"Type: {res.get('type_aav', 'N/A')}\n"
                f"Evaluation: {res.get('type_evaluation', 'N/A')}\n"
                f"Prerequis: {prerequis_ids_str}\n"
                f"Prerequis Externes: {prerequis_externes_str}\n"
                f"Status: {'Actif' if res.get('is_active', True) else 'Inactif'}\n"
            )

            self.affichage_resultat.value = details_text
            self.affichage_resultat.color = "#212121"
            self.markdown_display.value = res.get('description_markdown') or "Aucune description technique."
            self.bouton_modifier.visible = True
            self.bouton_supprimer.visible = True
            self.bouton_graph.visible = True
            self.bouton_graph_interactif.visible = True
        elif response and response.status_code == 404:
            self.affichage_resultat.value = f"Referentiel introuvable (ID {aav_id})."
            self.affichage_resultat.color = "#F44336"
        else:
            self.affichage_resultat.value = "Erreur de communication avec le serveur."
            self.affichage_resultat.color = "#F44336"

        if self.page:
            self.page.update()

    def afficher_graphe(self, e):
        """Genere et affiche le graphe de dependances statique."""
        self.bouton_graph.icon = ft.Icons.HOURGLASS_EMPTY
        self.bouton_graph.text = "Generation..."
        self.page.update()

        try:
            from app.services.graph_service import generate_aav_dependency_graph
            b64_image = generate_aav_dependency_graph(int(self.aav_id))
            if b64_image:
                self.graph_image.src_base64 = b64_image
                self.graph_image.visible = True
                self.graph_display.visible = True
                self.bouton_graph.text = "Actualiser"
            else:
                self._set_result_error("Aucune relation identifiee pour ce referentiel.")
        except Exception as err:
            print(f"Erreur graphe: {err}")
        finally:
            self.bouton_graph.icon = ft.Icons.ACCOUNT_TREE
            self.page.update()

    def afficher_graphe_interactif(self, e):
        """Genere et ouvre le graphe interactif dans le navigateur par defaut."""
        self.bouton_graph_interactif.icon = ft.Icons.HOURGLASS_EMPTY
        self.page.update()

        try:
            from app.services.graph_service import generate_interactive_graph
            file_path = generate_interactive_graph(int(self.aav_id))
            if file_path:
                self.page.launch_url(f"file://{file_path}")
        except Exception as err:
            print(f"Erreur graphe interactif: {err}")
        finally:
            self.bouton_graph_interactif.icon = ft.Icons.WEB
            self.page.update()

    def ouvrir_popup_modifier(self, e):
        """Ouvre un dialogue d'edition pour mettre a jour les informations de l'AAV."""
        res_call = _get(f"/aavs/{self.aav_id}")
        if not res_call: return
        res = res_call.json()

        champ_nom = ft.TextField(label="Nom", value=res.get("nom", ""), width=400)
        champ_disc = ft.TextField(label="Discipline", value=res.get("discipline", ""), width=400)
        champ_ens = ft.TextField(label="Enseignement", value=res.get("enseignement", ""), width=400)
        champ_desc = ft.TextField(label="Description Markdown", value=res.get("description_markdown", ""), width=400, multiline=True, min_lines=5)

        def sauvegarder(ev):
            payload = {
                "nom": champ_nom.value, "discipline": champ_disc.value,
                "enseignement": champ_ens.value, "description_markdown": champ_desc.value
            }
            r = _put(f"/aavs/{self.aav_id}", payload)
            dialog.open = False
            if r and r.status_code == 200:
                self.charger_aav(self.aav_id, None)
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Modification Referentiel"),
            content=ft.Column([champ_nom, champ_disc, champ_ens, champ_desc], scroll=ft.ScrollMode.AUTO, tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Sauvegarder", on_click=sauvegarder, color="white", bgcolor="#4CAF50")
            ]
        )
        self.page.overlay.append(dialog); dialog.open = True; self.page.update()

    def action_supprimer(self, e):
        """Demande confirmation puis supprime definitivement le referentiel AAV."""
        def confirmer(ev):
            r = _delete(f"/aavs/{self.aav_id}")
            dialog.open = False
            if r and r.status_code == 200:
                self.show_about(None)
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmation de suppression"),
            content=ft.Text(f"Supprimer definitivement l'AAV #{self.aav_id} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Supprimer", on_click=confirmer, color="white", bgcolor="#F44336")
            ]
        )
        self.page.overlay.append(dialog); dialog.open = True; self.page.update()
