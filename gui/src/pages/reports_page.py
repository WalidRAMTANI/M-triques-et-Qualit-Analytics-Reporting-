import sys
import httpx
import base64
import json
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class ReportsPage:
    """
    Page de generation et de consultation des rapports d'analytics.
    Gere les bilans globaux, les fiches individuelles et l'exportation au format PDF.
    """

    def __init__(self, content_area):
        """Initialise la page et les composants de saisie d'identifiants."""
        self.content_area = content_area
        self._page = None
        self.champ_id = ft.TextField(
            label="Identifiant Cible (Apprenant, AAV ou Discipline)", 
            width=350, border_color="#B71C1C", 
            keyboard_type=ft.KeyboardType.TEXT, 
            hint_text="Saisissez un ID ou un nom"
        )
        self.result_container = ft.Container(
            expand=True, padding=20, border_radius=15, 
            border=ft.border.all(1, "#FFCDD2"), bgcolor="#FFFBFB"
        )

    def _set_result(self, control: ft.Control):
        """Met a jour la zone d'affichage des resultats du rapport."""
        self.result_container.content = control
        if self._page:
            self._page.update()

    def _create_stat_card(self, label, value, icon, color):
        """Genere une carte visuelle pour l'affichage d'un indicateur cle (KPI)."""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=30),
                ft.Text(value, size=24, weight="bold", color=color),
                ft.Text(label, size=12, color="grey", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor="white", padding=20, border_radius=12,
            border=ft.border.all(1, "#EEEEEE"), width=160
        )

    def load_global(self, e):
        """Charge et affiche le rapport de synthese global du systeme."""
        self._set_result(ft.ProgressRing(color="#B71C1C"))
        try:
            r = httpx.get(f"{BASE_URL}/reports/global", timeout=15)
            if r.status_code == 200:
                data = r.json()
                stats = data.get("contenu", {})
                
                header = ft.Column([
                    ft.Text(data.get("titre", "Tableau de Bord Global"), size=24, weight="bold", color="#B71C1C"),
                    ft.Text(f"Generation : {data.get('date_generation', '---')[:16]}", size=13, italic=True),
                    ft.Divider(height=20, color="#FFCDD2"),
                ])

                kpis = ft.Row([
                    self._create_stat_card("AAVs Totaux", str(stats.get("nb_aavs_total", 0)), ft.Icons.ACCOUNT_TREE, "#B71C1C"),
                    self._create_stat_card("Utilisables", str(stats.get("nb_aavs_utilisables", 0)), ft.Icons.CHECK_CIRCLE, "#2E7D32"),
                    self._create_stat_card("Alertes", str(stats.get("nb_alertes", {}).get("difficiles", 0)), ft.Icons.WARNING_AMBER, "#EF6C00"),
                ], wrap=True, alignment=ft.MainAxisAlignment.CENTER)

                rows = []
                for k, v in stats.items():
                    if k in ["aavs_data", "alertes", "nb_alertes", "nb_aavs_total", "nb_aavs_utilisables"]: continue
                    rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(k).replace("_", " ").title())), ft.DataCell(ft.Text(str(v)))]))

                self._set_result(ft.Column([
                    header, kpis, 
                    ft.DataTable(columns=[ft.DataColumn(ft.Text("Metrique")), ft.DataColumn(ft.Text("Valeur"))], rows=rows)
                ], scroll=ft.ScrollMode.AUTO, expand=True))
            else:
                self._set_result(ft.Text(f"Erreur Serveur: {r.status_code}"))
        except Exception as err:
            self._set_result(ft.Text(f"Erreur Technique: {err}"))

    def load_specific(self, rtype):
        """Demande la generation d'un rapport specifique (Apprenant, AAV, Discipline) en JSON."""
        if not self.champ_id.value:
            self._set_result(ft.Text("Identifiant requis.")); return
        
        self._set_result(ft.ProgressRing(color="#B71C1C"))
        try:
            payload = {"type_rapport": rtype, "id_cible": self.champ_id.value, "format": "json"}
            r = httpx.post(f"{BASE_URL}/reports/generate", json=payload, timeout=15)
            if r.status_code in [200, 201]:
                report = r.json()
                content = report.get("contenu", "{}")
                if isinstance(content, str):
                    try: content = json.loads(content)
                    except: pass
                
                rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(k))), ft.DataCell(ft.Text(str(v)))]) for k, v in content.items() if not isinstance(v, (dict, list))]
                self._set_result(ft.Column([
                    ft.Text(f"Analyse {rtype.title()} - {self.champ_id.value}", size=20, weight="bold", color="#B71C1C"),
                    ft.DataTable(columns=[ft.DataColumn(ft.Text("Propriete")), ft.DataColumn(ft.Text("Valeur"))], rows=rows)
                ], scroll=ft.ScrollMode.AUTO))
            else:
                self._set_result(ft.Text("Pas de donnees pour cette cible."))
        except Exception as err:
            self._set_result(ft.Text(f"Erreur : {err}"))

    def load_pdf(self, rtype):
        """Genere un rapport PDF et l'enregistre localement sur le poste utilisateur."""
        if not self.champ_id.value:
            self._set_result(ft.Text("Identifiant requis.")); return
        
        self._set_result(ft.ProgressRing(color="#B71C1C"))
        try:
            payload = {"type_rapport": rtype, "id_cible": self.champ_id.value, "format": "pdf"}
            r = httpx.post(f"{BASE_URL}/reports/generate", json=payload, timeout=20)
            if r.status_code in [200, 201]:
                report = r.json()
                export_dir = Path(PROJECT_ROOT) / "exports"
                export_dir.mkdir(exist_ok=True)
                filepath = export_dir / f"Rapport_{rtype}_{self.champ_id.value}.pdf"
                
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(report.get("contenu")))
                
                self._page.snack_bar = ft.SnackBar(ft.Text(f"Export PDF reussi : {filepath}"), bgcolor="green")
                self._page.snack_bar.open = True
                self._set_result(ft.Text(f"Fichier exporte : {filepath}", color="green"))
                self._page.update()
            else:
                self._set_result(ft.Text(f"Echec du serveur (Code {r.status_code})"))
        except Exception as err:
            self._set_result(ft.Text(f"Erreur technique : {err}"))

    def build(self, page: ft.Page):
        """Genere le layout de la page de rapports."""
        self._page = page

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.Icons.QUERY_STATS, color="white", size=30), bgcolor="#B71C1C", padding=10, border_radius=10),
                    ft.Text("Reporting et Analyses Pedago", size=26, weight="bold", color="#B71C1C"),
                ]),
                ft.Row([
                    self.champ_id,
                    ft.ElevatedButton("Rapport Global", on_click=self.load_global, bgcolor="#B71C1C", color="white", height=50),
                ], spacing=10),
                
                ft.Text("Analyses Rapides :", size=14, weight="bold"),
                ft.Row([
                    ft.ElevatedButton("Apprenant", icon=ft.Icons.PERSON, on_click=lambda _: self.load_specific("student"), bgcolor="#D32F2F", color="white"),
                    ft.ElevatedButton("AAV", icon=ft.Icons.HISTORY, on_click=lambda _: self.load_specific("aav"), bgcolor="#E53935", color="white"),
                    ft.ElevatedButton("Discipline", icon=ft.Icons.BOOK, on_click=lambda _: self.load_specific("discipline"), bgcolor="#f44336", color="white"),
                ], wrap=True, spacing=10),
                
                ft.Text("Export PDF :", size=14, weight="bold", color="#B71C1C"),
                ft.Row([
                    ft.ElevatedButton("PDF Apprenant", icon=ft.Icons.PICTURE_AS_PDF, on_click=lambda _: self.load_pdf("student"), bgcolor="#FFC107", color="black"),
                    ft.ElevatedButton("PDF AAV", icon=ft.Icons.PICTURE_AS_PDF, on_click=lambda _: self.load_pdf("aav"), bgcolor="#FFC107", color="black"),
                    ft.ElevatedButton("PDF Discipline", icon=ft.Icons.PICTURE_AS_PDF, on_click=lambda _: self.load_pdf("discipline"), bgcolor="#FFC107", color="black"),
                ], wrap=True, spacing=10),
                
                ft.Divider(height=20),
                self.result_container
            ], spacing=20, scroll=ft.ScrollMode.AUTO),
            padding=30, expand=True
        )
