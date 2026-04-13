"""
AAV Detail page for displaying comprehensive AAV information.

Shows detailed view of a single AAV with full information,
modify and delete capabilities, styled with William GUI aesthetics.
"""

import sys
from pathlib import Path
import flet as ft

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .../projet_python
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.routers import aavs
from app.database import SessionLocal


class DetailsPage:
    """Detailed view of a single AAV with edit and delete capabilities."""
    
    def __init__(self, content_area, show_about_callback):
        """
        Initialize the AAV Details Page.
        
        Args:
            content_area (ft.Column): Container for page content
            show_about_callback (callable): Callback function to navigate back to about page
        
        Returns:
            None
        """
        self.content_area = content_area
        self.show_about = show_about_callback
        self.page_content = None
        self.page = None
        self.aav_id = None
        self.affichage_resultat = None
        self.bouton_modifier = None
        self.bouton_supprimer = None
    
    def build(self, aav_id, page):
        """
        Build and return the detailed AAV information page.
        
        Fetches complete AAV data from the database and constructs a comprehensive
        details page displaying AAV information in William GUI style with white background,
        including edit and delete buttons.
        
        Args:
            aav_id (int or str): Unique identifier of the AAV to display
            page (ft.Page): The Flet page object for UI rendering
        
        Returns:
            ft.Container: Complete details page UI with all AAV information
        
        Side Effects:
            - Fetches AAV data from database
            - Stores page reference for updates
        """
        self.page = page
        self.aav_id = aav_id
        
        # Initialize display elements
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
        
        boite_resultat = ft.Container(
            content=self.affichage_resultat,
            width=700,
            height=400,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
        )
        
        # Load AAV data
        self.charger_aav(aav_id, boite_resultat)
        
        # Header with title and back button
        header = ft.Row([
            ft.Text(f"Détails AAV #{aav_id}", size=28, weight="bold", color="#1565C0", expand=True),
            ft.ElevatedButton("Back to About", on_click=self.show_about, color="#FFFFFF", bgcolor="#1565C0"),
        ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.page_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20, color="transparent"),
                boite_resultat,
                ft.Divider(height=15, color="transparent"),
                ft.Row(
                    [self.bouton_modifier, self.bouton_supprimer],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                ft.Divider(height=20, color="transparent"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, scroll=ft.ScrollMode.AUTO),
            bgcolor="#F5F5F5",
            expand=True,
            padding=20,
        )
        
        return self.page_content
    
    def charger_aav(self, aav_id, boite_resultat):
        """
        Load AAV data from database and display it.
        
        Args:
            aav_id (int or str): AAV identifier
            boite_resultat (ft.Container): Container to update with results
        """
        db = SessionLocal()
        try:
            res = aavs.get_aav(int(aav_id), db)
            
            # Format prerequis_ids list
            prerequis_ids = res.get('prerequis_ids', [])
            prerequis_ids_str = ", ".join(map(str, prerequis_ids)) if prerequis_ids else "Aucun"
            
            # Format prerequis_externes_codes list
            prerequis_externes = res.get('prerequis_externes_codes', [])
            prerequis_externes_str = ", ".join(prerequis_externes) if prerequis_externes else "Aucun"
            
            # Format all details
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
                f"Description:\n{res.get('description_markdown', 'N/A')}\n"
            )
            
            self.affichage_resultat.value = details_text
            self.affichage_resultat.color = "#212121"
            self.bouton_modifier.visible = True
            self.bouton_supprimer.visible = True
            
        except Exception as e:
            self.affichage_resultat.value = f"Erreur: AAV #{aav_id} non trouvé"
            self.affichage_resultat.color = "#F44336"
            self.bouton_modifier.visible = False
            self.bouton_supprimer.visible = False
            print(f"Erreur chargement AAV: {e}")
        finally:
            db.close()
            self.page.update()
    
    def ouvrir_popup_modifier(self, e):
        """
        Open a dialog to modify AAV information.
        
        Args:
            e: Click event
        """
        try:
            db = SessionLocal()
            res = aavs.get_aav(int(self.aav_id), db)
            db.close()
            
            # Create text fields with current values
            champ_nom = ft.TextField(label="Nom", value=res.get("nom", ""), width=400)
            champ_libelle = ft.TextField(label="Libellé Integration", value=res.get("libelle_integration", ""), width=400)
            champ_discipline = ft.TextField(label="Discipline", value=res.get("discipline", ""), width=400)
            champ_enseignement = ft.TextField(label="Enseignement", value=res.get("enseignement", ""), width=400)
            champ_type_aav = ft.TextField(label="Type AAV", value=res.get("type_aav", ""), width=400)
            champ_type_eval = ft.TextField(label="Type Evaluation", value=res.get("type_evaluation", ""), width=400)
            champ_desc = ft.TextField(
                label="Description",
                value=res.get("description_markdown", ""),
                width=400,
                min_lines=5,
                max_lines=10
            )

            def sauvegarder(ev):
                db2 = SessionLocal()
                try:
                    nouvelles_donnees = {
                        "nom": champ_nom.value,
                        "libelle_integration": champ_libelle.value,
                        "discipline": champ_discipline.value,
                        "enseignement": champ_enseignement.value,
                        "type_aav": champ_type_aav.value,
                        "type_evaluation": champ_type_eval.value,
                        "description_markdown": champ_desc.value
                    }
                    aavs.update_aav(int(self.aav_id), nouvelles_donnees, db2)
                    self.affichage_resultat.value = "✅ AAV modifié avec succès"
                    self.affichage_resultat.color = "#4CAF50"
                except Exception as err:
                    self.affichage_resultat.value = f"❌ Erreur: {str(err)}"
                    self.affichage_resultat.color = "#F44336"
                finally:
                    db2.close()
                    dialog.open = False
                    self.page.update()
                    self.charger_aav(self.aav_id, None)
                
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
            
        except Exception as error:
            print(f"ERREUR POPUP: {error}")
            self.affichage_resultat.value = f"❌ Erreur: {str(error)}"
            self.affichage_resultat.color = "#F44336"
            self.page.update()

    def action_supprimer(self, e):
        """
        Delete the AAV after confirmation.
        
        Args:
            e: Click event
        """
        def confirmer_suppression(ev):
            db = SessionLocal()
            try:
                aavs.delete_aav(int(self.aav_id), db)
                self.affichage_resultat.value = "✅ AAV supprimé avec succès"
                self.affichage_resultat.color = "#4CAF50"
                self.bouton_modifier.visible = False
                self.bouton_supprimer.visible = False
            except Exception as error:
                self.affichage_resultat.value = f"❌ Erreur suppression: {str(error)}"
                self.affichage_resultat.color = "#F44336"
                print(f"ERREUR SUPPRESSION: {error}")
            finally:
                db.close()
                dialog.open = False
                self.page.update()
        
        def annuler(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Confirmer la suppression", size=20, weight="bold"),
            content=ft.Text(f"Êtes-vous sûr de vouloir supprimer AAV #{self.aav_id} ?"),
            actions=[
                ft.TextButton("Annuler", on_click=annuler),
                ft.ElevatedButton("Supprimer", on_click=confirmer_suppression, color="#FFFFFF", bgcolor="#F44336")
            ]
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
