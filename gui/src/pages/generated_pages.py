import flet as ft
from utils import fetch

class GenericEndpointPage:
    def __init__(self, content_area, title, endpoints):
        self.content_area = content_area
        self.title = title
        self.endpoints = endpoints

    def build(self, page):
        self._page = page
        
        output_txt = ft.Text("Résultat JSON de la requête s'affichera ici...", size=12, selectable=True)
        output_container = ft.Container(
            content=ft.Column([output_txt], scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE10,
            border_radius=8,
            padding=16,
            height=300,
            expand=True
        )

        def make_button(ep_path, ep_method):
            input_fields = []
            import re
            params = re.findall(r"\{([^}]+)\}", ep_path)
            param_controls = {}
            for param in params:
                tf = ft.TextField(label=param, width=150, dense=True)
                param_controls[param] = tf
                input_fields.append(tf)

            def on_click(e):
                final_path = ep_path
                for p, tf in param_controls.items():
                    val = tf.value if tf.value else "1"
                    final_path = final_path.replace(f"{{{p}}}", val)
                
                # Fetch only works for GET easily in Flet without full httpx wrapper,
                # but we can try to do a generic fetch using the base endpoint
                try:
                    import httpx
                    url = f"http://localhost:8000{final_path}"
                    if ep_method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        # For mock purposes we just simulate GET or generic HTTP
                        r = httpx.request(ep_method, url, timeout=5)
                        try:
                            res = r.json()
                        except:
                            res = r.text
                        import json
                        output_txt.value = json.dumps(res, indent=2, ensure_ascii=False)
                    else:
                        output_txt.value = f"Méthode {ep_method} non supportée par le wrapper simple."
                except Exception as ex:
                    output_txt.value = f"Erreur: {str(ex)}"
                self._page.update()

            return ft.Container(
                content=ft.Column([
                    ft.Text(f"{ep_method} {ep_path}", weight=ft.FontWeight.W_600),
                    ft.Row(input_fields + [
                        ft.ElevatedButton("Exécuter", on_click=on_click, bgcolor="#9C27B0", color=ft.Colors.WHITE)
                    ], wrap=True)
                ]),
                bgcolor=ft.Colors.WHITE10,
                border_radius=8,
                padding=12,
                margin=ft.margin.only(bottom=8)
            )

        buttons = []
        for ep, methods in self.endpoints.items():
            for method in methods:
                if method != 'HEAD':
                    buttons.append(make_button(ep, method))

        page_content = ft.Column([
            ft.Text(self.title, size=24, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            ft.Text("Testeur de endpoints API généré dynamiquement", color=ft.Colors.WHITE54, size=13),
            ft.Divider(color=ft.Colors.WHITE24),
            ft.Column(buttons, spacing=4),
            ft.Divider(color=ft.Colors.WHITE24),
            ft.Text("Output API :", size=16),
            output_container
        ], scroll=ft.ScrollMode.AUTO, expand=True)

        return page_content

# Configuration of missing pages based on OpenAPI endpoints

MISSING_PAGES_CONFIG = {
    "Activités Pédagogiques": {
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
    "Apprenants": {
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
    "Comparaison": {
        "/metrics/compare/aavs": ["GET"],
        "/metrics/compare/learners": ["GET"],
    },
    "Moteur d'Exercices": {
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
    "Navigation": {
        "/navigation/{id_apprenant}/accessible": ["GET"],
        "/navigation/{id_apprenant}/in-progress": ["GET"],
        "/navigation/{id_apprenant}/blocked": ["GET"],
        "/navigation/{id_apprenant}/reviewable": ["GET"],
        "/navigation/{id_apprenant}/dashboard": ["GET"],
        "/navigation/{id_apprenant}": ["GET"],
    },
    "Ontologies": {
        "/ontologies/": ["GET", "POST"],
        "/ontologies/{id_reference}": ["GET", "PUT", "DELETE"],
    },
    "Fabrication Prompts (CRUD)": {
        "/prompts/": ["GET", "POST"],
        "/prompts/{id_prompt}": ["GET", "PUT", "PATCH", "DELETE"],
    },
    "Remédiation": {
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
    "Rapports": {
        "/reports/generate": ["POST"],
        "/reports/global": ["GET"],
    },
    "Statuts Apprentissage": {
        "/learning-status": ["GET", "POST"],
        "/learning-status/{statut_id}": ["GET", "PUT"],
        "/learning-status/{statut_id}/mastery": ["PATCH"],
        "/learning-status/{id}/attempts": ["GET"],
        "/learning-status/{id}/attempts/timeline": ["GET"],
        "/learning-status/{id}/reset": ["POST"],
    },
    "Tentatives": {
        "/attempts": ["GET", "POST"],
        "/attempts/{id}": ["GET", "DELETE"],
        "/attempts/{id}/process": ["POST"],
    },
    "Types & Dictionnaires": {
        "/types/activity-types": ["GET"],
        "/types/mastery-levels": ["GET"],
        "/types/disciplines": ["GET"],
    }
}
