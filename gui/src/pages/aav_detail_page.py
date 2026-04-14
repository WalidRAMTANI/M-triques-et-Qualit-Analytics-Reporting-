"""
AAV Detail page — consomme l'API REST via HTTP (httpx).
Endpoints : GET/PUT/DELETE /aavs/{id}
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .../projet_python
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft
import httpx

BASE_URL = "http://localhost:8000"


def _get(path: str):
    try:
        r = httpx.get(f"{BASE_URL}{path}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"[GET] {path} → {e}")
        return None


def _put(path: str, payload: dict):
    try:
        r = httpx.put(f"{BASE_URL}{path}", json=payload, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"[PUT] {path} → {e}")
        return None


def _delete(path: str):
    try:
        r = httpx.delete(f"{BASE_URL}{path}", timeout=5)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"[DELETE] {path} → {e}")
        return False


class DetailsPage:
    """Detailed view of a single AAV with edit and delete capabilities."""

    def __init__(self, content_area, show_about_callback):
        """
        Initialize the AAV Details Page.

        Args:
            content_area (ft.Column): Container for page content
            show_about_callback (callable): Callback function to navigate back to about page
        """
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
        """
        Build and return the detailed AAV information page.

        Args:
            aav_id (int or str): Unique identifier of the AAV to display
            page (ft.Page): The Flet page object for UI rendering

        Returns:
            ft.Container: Complete details page UI with all AAV information
        """
        self.page = page
        self.aav_id = aav_id

        self.affichage_resultat = ft.Text("Chargement...", size=14, color="#212121")

        self.bouton_modifier = ft.ElevatedButton(
            "Modifier",
            visible=False,
            on_click=self.ouvrir_popup_modifier,
            color="#FFFFFF",
            bgcolor="#2196F3"
        )
        self.bouton_supprimer = ft.ElevatedButton(
            "Supprimer",
            visible=False,
            on_click=self.action_supprimer,
            color="#FFFFFF",
            bgcolor="#F44336"
        )
        self.bouton_graph = ft.ElevatedButton(
            "Visualiser Graphe",
            icon=ft.Icons.ACCOUNT_TREE,
            visible=False,
            on_click=self.afficher_graphe,
            color="#FFFFFF",
            bgcolor="#4CAF50"
        )
        self.bouton_graph_interactif = ft.ElevatedButton(
            "Graphe Interactif",
            icon=ft.Icons.WEB,
            visible=False,
            on_click=self.afficher_graphe_interactif,
            color="#FFFFFF",
            bgcolor="#9C27B0",
            tooltip="Ouvrir le graphe interactif (PyVis) dans le navigateur"
        )

        self.markdown_display = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: page.launch_url(e.data),
        )

        self.graph_image = ft.Image(src_base64="", visible=False, border_radius=10)
        self.graph_display = ft.Container(
            content=self.graph_image,
            visible=False,
            alignment=ft.alignment.center,
            padding=10,
            border=ft.border.all(1, "#E0E0E0"),
            border_radius=10,
        )

        boite_resultat = ft.Container(
            content=ft.Column([
                self.affichage_resultat,
                ft.Divider(height=10),
                ft.Text("Description Markdown :", weight="bold", size=16),
                ft.Container(
                    content=self.markdown_display,
                    padding=10,
                    bgcolor="#F9F9F9",
                    border_radius=5,
                ),
                ft.Divider(height=10),
                self.graph_display
            ], scroll=ft.ScrollMode.AUTO),
            width=750,
            height=500,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            shadow=ft.BoxShadow(blur_radius=10, color="#D0D0D0")
        )

        self.charger_aav(aav_id, boite_resultat)

        header = ft.Row([
            ft.Text(f"Détails AAV #{aav_id}", size=28, weight="bold", color="#1565C0", expand=True),
            ft.ElevatedButton("Retour", on_click=self.show_about, color="#FFFFFF", bgcolor="#1565C0"),
        ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.page_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20, color="transparent"),
                boite_resultat,
                ft.Divider(height=15, color="transparent"),
                ft.Row(
                    [self.bouton_modifier, self.bouton_supprimer, self.bouton_graph, self.bouton_graph_interactif],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    wrap=True,
                ),
                ft.Divider(height=20, color="transparent"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, scroll=ft.ScrollMode.AUTO),
            bgcolor="#F5F5F5",
            expand=True,
            padding=20,
        )

        return self.page_content

    def charger_aav(self, aav_id, boite_resultat):
        """Load AAV data from the REST API and display it."""
        res = _get(f"/aavs/{aav_id}")

        if res and "id_aav" in res:
            prerequis_ids = res.get('prerequis_ids') or []
            prerequis_ids_str = ", ".join(map(str, prerequis_ids)) if prerequis_ids else "Aucun"
            prerequis_externes = res.get('prerequis_externes_codes') or []
            prerequis_externes_str = ", ".join(prerequis_externes) if prerequis_externes else "Aucun"

            details_text = (
                f"ID AAV: {res.get('id_aav', 'N/A')}\n"
                f"Nom: {res.get('nom', 'N/A')}\n"
                f"Libelle Integration: {res.get('libelle_integration', 'N/A')}\n"
                f"Discipline: {res.get('discipline', 'N/A')}\n"
                f"Enseignement: {res.get('enseignement', 'N/A')}\n"
                f"Type AAV: {res.get('type_aav', 'N/A')}\n"
                f"Type Evaluation: {res.get('type_evaluation', 'N/A')}\n"
                f"Prerequis IDs: {prerequis_ids_str}\n"
                f"Prerequis Externes: {prerequis_externes_str}\n"
                f"Version: {res.get('version', 'N/A')}\n"
                f"Status: {'Active' if res.get('is_active', True) else 'Inactive'}\n"
            )

            self.affichage_resultat.value = details_text
            self.affichage_resultat.color = "#212121"
            self.markdown_display.value = res.get('description_markdown') or "Aucune description"
            self.bouton_modifier.visible = True
            self.bouton_supprimer.visible = True
            self.bouton_graph.visible = True
            self.bouton_graph_interactif.visible = True
            self.graph_display.visible = False
            self.graph_image.visible = False
        else:
            self.affichage_resultat.value = f"❌ AAV #{aav_id} non trouvé (vérifiez que le serveur tourne)"
            self.affichage_resultat.color = "#F44336"
            self.bouton_modifier.visible = False
            self.bouton_supprimer.visible = False

        self.page.update()

    def afficher_graphe(self, e):
        """Generates and displays the static matplotlib dependency graph."""
        self.bouton_graph.icon = ft.Icons.HOURGLASS_EMPTY
        self.bouton_graph.text = "Génération..."
        self.page.update()

        try:
            # Import local graph service (still uses DB directly — OK for graph rendering)
            from app.services.graph_service import generate_aav_dependency_graph
            b64_image = generate_aav_dependency_graph(int(self.aav_id))
            if b64_image:
                self.graph_image.src_base64 = b64_image
                self.graph_image.visible = True
                self.graph_display.visible = True
                self.bouton_graph.text = "Graphe mis à jour"
            else:
                self.affichage_resultat.value += "\n(Pas de relations à afficher)"
        except Exception as err:
            print(f"Erreur graphe: {err}")
            self.affichage_resultat.value += f"\nErreur Graphe: {err}"
        finally:
            self.bouton_graph.icon = ft.Icons.ACCOUNT_TREE
            self.bouton_graph.text = "Visualiser Graphe"
            self.page.update()

    def afficher_graphe_interactif(self, e):
        """Generates and opens the interactive pyvis graph."""
        self.bouton_graph_interactif.icon = ft.Icons.HOURGLASS_EMPTY
        self.bouton_graph_interactif.text = "Génération..."
        self.page.update()

        try:
            from app.services.graph_service import generate_interactive_graph
            file_path = generate_interactive_graph(int(self.aav_id))
            if file_path:
                self.page.launch_url(f"file://{file_path}")
                self.affichage_resultat.value += "\n✅ Graphe interactif ouvert dans le navigateur !"
            else:
                self.affichage_resultat.value += "\n(Pas de relations à afficher)"
        except Exception as err:
            print(f"Erreur graphe interactif: {err}")
            self.affichage_resultat.value += f"\nErreur Graphe Interactif: {err}"
        finally:
            self.bouton_graph_interactif.icon = ft.Icons.WEB
            self.bouton_graph_interactif.text = "Graphe Interactif"
            self.page.update()

    def ouvrir_popup_modifier(self, e):
        """Open a dialog to modify AAV information."""
        res = _get(f"/aavs/{self.aav_id}")
        if not res:
            self.affichage_resultat.value = "❌ Impossible de charger les données pour modification"
            self.affichage_resultat.color = "#F44336"
            self.page.update()
            return

        champ_nom = ft.TextField(label="Nom", value=res.get("nom", ""), width=400)
        champ_libelle = ft.TextField(label="Libellé Integration", value=res.get("libelle_integration", ""), width=400)
        champ_discipline = ft.TextField(label="Discipline", value=res.get("discipline", ""), width=400)
        champ_enseignement = ft.TextField(label="Enseignement", value=res.get("enseignement", ""), width=400)
        champ_type_aav = ft.TextField(label="Type AAV", value=res.get("type_aav", ""), width=400)
        champ_type_eval = ft.TextField(label="Type Evaluation", value=res.get("type_evaluation", ""), width=400)
        champ_desc = ft.TextField(
            label="Description Markdown",
            value=res.get("description_markdown", ""),
            width=400,
            min_lines=5,
            max_lines=10
        )

        def sauvegarder(ev):
            nouvelles_donnees = {
                "nom": champ_nom.value,
                "libelle_integration": champ_libelle.value,
                "discipline": champ_discipline.value,
                "enseignement": champ_enseignement.value,
                "type_aav": champ_type_aav.value,
                "type_evaluation": champ_type_eval.value,
                "description_markdown": champ_desc.value
            }
            result = _put(f"/aavs/{self.aav_id}", nouvelles_donnees)
            dialog.open = False
            if result:
                self.affichage_resultat.value = "✅ AAV modifié avec succès"
                self.affichage_resultat.color = "#4CAF50"
                self.page.update()
                self.charger_aav(self.aav_id, None)
            else:
                self.affichage_resultat.value = "❌ Erreur lors de la modification"
                self.affichage_resultat.color = "#F44336"
                self.page.update()

        def annuler(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier AAV n°{self.aav_id}", size=20, weight="bold"),
            content=ft.Column([
                champ_nom, champ_libelle, champ_discipline,
                champ_enseignement, champ_type_aav, champ_type_eval, champ_desc
            ], scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Annuler", on_click=annuler),
                ft.ElevatedButton("Sauvegarder", on_click=sauvegarder, color="#FFFFFF", bgcolor="#4CAF50")
            ]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def action_supprimer(self, e):
        """Delete the AAV after confirmation."""

        def confirmer_suppression(ev):
            ok = _delete(f"/aavs/{self.aav_id}")
            dialog.open = False
            if ok:
                self.affichage_resultat.value = "✅ AAV supprimé avec succès"
                self.affichage_resultat.color = "#4CAF50"
                self.bouton_modifier.visible = False
                self.bouton_supprimer.visible = False
                self.bouton_graph.visible = False
                self.bouton_graph_interactif.visible = False
            else:
                self.affichage_resultat.value = "❌ Erreur lors de la suppression"
                self.affichage_resultat.color = "#F44336"
            self.page.update()

        def annuler(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression", size=20, weight="bold"),
            content=ft.Text(f"Êtes-vous sûr de vouloir supprimer AAV #{self.aav_id} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=annuler),
                ft.ElevatedButton("Supprimer", on_click=confirmer_suppression, color="#FFFFFF", bgcolor="#F44336")
            ]
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
