import flet as ft
import json
import httpx
import re

class GenericEndpointPage:
    """
    Page generateur dynamique de tests pour les points de terminaison API.
    Permet l'exploration recursive et le test unitaire des routes definies dans le referentiel OpenAPI.
    """

    def __init__(self, content_area, title, endpoints):
        """Initialise le testeur avec une liste de routes et leurs methodes associees."""
        self.content_area = content_area
        self.title = title
        self.endpoints = endpoints
        self._page = None

    def build(self, page):
        """Construit l'interface graphique du bac a sable API."""
        self._page = page
        
        output_txt = ft.Text("Le flux JSON de retour s'affichera ici apres execution.", size=12, selectable=True)
        output_container = ft.Container(
            content=ft.Column([output_txt], scroll=ft.ScrollMode.AUTO),
            bgcolor="#F5F5F5", border_radius=8, padding=16, height=300, expand=True,
            border=ft.border.all(1, "#E0E0E0")
        )

        def make_button(ep_path, ep_method):
            """Genere dynamiquement un composant de test pour une route specifique."""
            input_fields = []
            params = re.findall(r"\{([^}]+)\}", ep_path)
            param_controls = {}
            for param in params:
                tf = ft.TextField(label=f"Parametre: {param}", width=150, dense=True, border_radius=8)
                param_controls[param] = tf
                input_fields.append(tf)

            def on_click(e):
                final_path = ep_path
                for p, tf in param_controls.items():
                    val = tf.value if tf.value else "1"
                    final_path = final_path.replace(f"{{{p}}}", val)
                
                try:
                    url = f"http://localhost:8000{final_path}"
                    if ep_method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        r = httpx.request(ep_method, url, timeout=10)
                        try:
                            res = r.json()
                        except:
                            res = r.text
                        output_txt.value = json.dumps(res, indent=2, ensure_ascii=False)
                    else:
                        output_txt.value = f"Methode {ep_method} non prise en charge."
                except Exception as ex:
                    output_txt.value = f"Erreur de communication : {str(ex)}"
                self._page.update()

            return ft.Container(
                content=ft.Column([
                    ft.Text(f"{ep_method} {ep_path}", weight=ft.FontWeight.W_600, color="#4A148C"),
                    ft.Row(input_fields + [
                        ft.ElevatedButton("Executer Requete", on_click=on_click, bgcolor="#7B1FA2", color="white")
                    ], wrap=True)
                ]),
                bgcolor="white", border_radius=8, padding=12, margin=ft.margin.only(bottom=8),
                border=ft.border.all(1, "#F3E5F5")
            )

        buttons = [
            make_button(ep, method)
            for ep, methods in self.endpoints.items()
            for method in methods if method != 'HEAD'
        ]

        return ft.Column([
            ft.Text(self.title, size=24, weight=ft.FontWeight.W_600, color="#4A148C"),
            ft.Text("Explorateur dynamique des points de terminaison du systeme AAV.", color="grey", size=13),
            ft.Divider(color="#E1BEE7"),
            ft.Column(buttons, spacing=4),
            ft.Divider(color="#E1BEE7"),
            ft.Text("Flux de Sortie API :", size=16, weight="bold"),
            output_container
        ], scroll=ft.ScrollMode.AUTO, expand=True)

# Configuration de l'inventaire des routes base sur OpenAPI
MISSING_PAGES_CONFIG = {
    "Activites Academiques": {
        "/activites/types": ["GET"],
        "/activites/": ["GET", "POST"],
        "/activites/{activity_id}": ["GET", "PUT", "DELETE"],
        "/activites/{activity_id}/exercises": ["GET"],
        "/activites/{activity_id}/exercises/{exercise_id}": ["POST", "DELETE"],
        "/activites/{activity_id}/exercises/reorder": ["PUT"],
        "/activites/{activity_id}/start": ["POST"],
        "/activites/{activity_id}/submit-attempt": ["POST"],
        "/activites/{activity_id}/complete": ["POST"],
    },
    "Referentiel Apprenants": {
        "/learners/": ["GET", "POST"],
        "/learners/{id_apprenant}": ["GET", "PUT", "PATCH", "DELETE"],
        "/learners/{id_apprenant}/external-prerequisites": ["GET", "POST"],
        "/learners/{id_apprenant}/external-prerequisites/{code}": ["DELETE"],
        "/learners/{id_apprenant}/learning-status": ["GET"],
        "/learners/{id_apprenant}/learning-status/summary": ["GET"],
        "/learners/{id_apprenant}/ontologie": ["GET"],
        "/learners/{id_apprenant}/ontologie/{id_reference}/switch": ["POST"],
        "/learners/{id_apprenant}/progress": ["GET"],
    },
    "Analyse Comparaison": {
        "/metrics/compare/aavs": ["GET"],
        "/metrics/compare/learners": ["GET"],
    },
    "Moteur d'Exercices et IA": {
        "/aavs/{id_aav}/prompts": ["GET"],
        "/aavs/{id_aav}/prompts/best": ["GET"],
        "/aavs/{id_aav}/prompts/generate": ["POST"],
        "/progression-rules": ["GET"],
        "/progression-rules/{id_aav}": ["GET", "PUT"],
        "/next-exercise/{id_aav}": ["GET"],
        "/sequence/{id_apprenant}/{id_aav}": ["GET"],
        "/exercises/select": ["POST"],
        "/exercises/sequence": ["POST"],
        "/exercises/evaluate": ["POST"],
        "/prompts/{id_prompt}/preview": ["POST"],
        "/prompts/{id_prompt}/success-rate": ["GET"],
    },
    "Exploration Navigation": {
        "/navigation/{id_apprenant}/accessible": ["GET"],
        "/navigation/{id_apprenant}/in-progress": ["GET"],
        "/navigation/{id_apprenant}/blocked": ["GET"],
        "/navigation/{id_apprenant}/reviewable": ["GET"],
        "/navigation/{id_apprenant}/dashboard": ["GET"],
        "/navigation/{id_apprenant}": ["GET"],
    },
    "Structures Ontologiques": {
        "/ontologies/": ["GET", "POST"],
        "/ontologies/{id_reference}": ["GET", "PUT", "DELETE"],
    },
    "Gestion des Prompts (CRUD)": {
        "/prompts/": ["GET", "POST"],
        "/prompts/{id_prompt}": ["GET", "PUT", "PATCH", "DELETE"],
    },
    "Diagnostic et Remediation": {
        "/diagnostics/remediation": ["POST"],
        "/learners/{id_apprenant}/diagnostics": ["GET"],
        "/learners/{id_apprenant}/aavs/{id_aav}/root-causes": ["GET"],
        "/remediation/generate-path": ["POST"],
        "/diagnostics/analyze-path": ["POST"],
        "/learners/{id_apprenant}/weaknesses": ["GET"],
        "/remediation/activities/{id_diagnostic}": ["GET"],
        "/diagnostics/{id_diagnostic}/tree": ["GET"],
        "/learners/{id_apprenant}/progression-map": ["GET"],
    },
    "Reporting Institutionnel": {
        "/reports/generate": ["POST"],
        "/reports/global": ["GET"],
    },
    "Statuts d'Apprentissage": {
        "/learning-status": ["GET", "POST"],
        "/learning-status/{statut_id}": ["GET", "PUT"],
        "/learning-status/{statut_id}/mastery": ["PATCH"],
        "/learning-status/{id}/attempts": ["GET"],
        "/learning-status/{id}/attempts/timeline": ["GET"],
        "/learning-status/{id}/reset": ["POST"],
    },
    "Journal des Tentatives": {
        "/attempts": ["GET", "POST"],
        "/attempts/{id}": ["GET", "DELETE"],
        "/attempts/{id}/process": ["POST"],
    },
    "Typologies et Dictionnaires": {
        "/types/activity-types": ["GET"],
        "/types/mastery-levels": ["GET"],
        "/types/disciplines": ["GET"],
    }
}
