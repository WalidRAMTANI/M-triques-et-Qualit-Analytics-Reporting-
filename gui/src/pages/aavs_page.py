import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx
import json
import io
import base64
import networkx as nx
import matplotlib
import flet as ft
from pydantic import ValidationError
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from app.model.model import AAVCreate, RegleProgression, TypeAAV, TypeEvaluationAAV

BASE_URL = "http://127.0.0.1:8000"

class AavsPage:
    """
    Page de gestion et de visualisation des Acquis d'Apprentissage Vises (AAV).
    Propose une recherche filtree, des fiches detaillees et une analyse graphique de l'ontologie.
    """

    def __init__(self, content_area, is_professor=False):
        """Initialise les filtres, la zone de liste et le conteneur de details."""
        self.content_area = content_area
        self.is_professor = is_professor
        self._page = None
        self.all_aavs = []
        self.filtered_aavs = []
        
        self.search_field = ft.TextField(
            label="Recherche par intitulé", on_change=self.filter_data, 
            expand=True, prefix_icon=ft.Icons.SEARCH
        )
        self.discipline_filter = ft.Dropdown(
            label="Discipline", width=200, on_select=self.filter_data, 
            options=[ft.dropdown.Option("Toutes")]
        )
        self.type_filter = ft.Dropdown(
            label="Typologie", width=150, on_select=self.filter_data, 
            options=[
                ft.dropdown.Option("Tous"),
                ft.dropdown.Option("Atomique"),
                ft.dropdown.Option("Composite")
            ]
        )
        
        self.list_view = ft.ListView(expand=True, spacing=10, padding=10)
        self.detail_container = ft.Container(
            expand=True, padding=20, border_radius=12, 
            bgcolor="#FFFFFF", border=ft.border.all(1, "#E3F2FD"),
            content=ft.Column([ft.Text("Veuillez selectionner un referentiel.", italic=True, color="grey")], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.selected_id = None

    def _set_detail(self, control: ft.Control):
        """Met a jour la zone d'affichage detaillee avec le composant fourni."""
        self.detail_container.content = control
        if self._page:
            self._page.update()

    def load_data(self, e=None):
        """Charge l'integralite du referentiel AAV via l'API REST."""
        try:
            r = httpx.get(f"{BASE_URL}/aavs/", timeout=10)
            if r.status_code == 200:
                self.all_aavs = r.json()
                disciplines = sorted(list(set(a.get("discipline") for a in self.all_aavs if a.get("discipline"))))
                self.discipline_filter.options = [ft.dropdown.Option("Toutes")] + [ft.dropdown.Option(d) for d in disciplines]
                self.filter_data(None)
        except Exception as err:
            print(f"Erreur chargement referentiel : {err}")

    def filter_data(self, e):
        """Filtre la liste locale des AAV en fonction des criteres saisis."""
        search = self.search_field.value.lower() if self.search_field.value else ""
        disc = self.discipline_filter.value
        atype = self.type_filter.value
        
        self.filtered_aavs = []
        for a in self.all_aavs:
            if search and search not in a.get("nom", "").lower(): continue
            if disc and disc != "Toutes" and a.get("discipline") != disc: continue
            is_composite = bool(a.get("enfants_ids") or a.get("type_aav") == "composite")
            if atype == "Atomique" and is_composite: continue
            if atype == "Composite" and not is_composite: continue
            self.filtered_aavs.append(a)
        self.update_list()

    def update_list(self):
        """Actualise visuellement la liste des acquis dans le menu lateral."""
        items = []
        for a in self.filtered_aavs:
            is_comp = bool(a.get("enfants_ids"))
            is_selected = self.selected_id == a["id_aav"]
            items.append(ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.SUBDIRECTORY_ARROW_RIGHT if is_comp else ft.Icons.RADIO_BUTTON_CHECKED, 
                    color="#1565C0" if not is_comp else "#6A1B9A"
                ),
                title=ft.Text(a.get("nom", f"AAV #{a['id_aav']}"), weight="bold"),
                subtitle=ft.Text(f"{a.get('discipline')} | {a.get('enseignement')}"),
                trailing=ft.Text(f"#{a['id_aav']}", size=12, color="grey"),
                bgcolor="#E3F2FD" if is_selected else None,
                on_click=lambda e, aav=a: self.show_detail(aav)
            ))
        self.list_view.controls = items
        if self._page:
            self._page.update()

    def show_detail(self, a_summary):
        """Affiche les details d'un AAV et prepare les options de visualisation graphique."""
        try:
            r = httpx.get(f"{BASE_URL}/aavs/{a_summary['id_aav']}", timeout=10)
            a = r.json() if r.status_code == 200 else a_summary
        except:
            a = a_summary

        self.selected_id = a["id_aav"]
        self.update_list()
        desc = a.get("description_markdown") or "Aucune description technique disponible."
        
        content = ft.Column([
            ft.Row([
                ft.Text(a.get("nom", ""), size=22, weight="bold", color="#1565C0", expand=True),
                ft.Chip(label=ft.Text(f"REF: {a['id_aav']}"), bgcolor="#E3F2FD")
            ]),
            ft.Row([ft.Icon(ft.Icons.SCHOOL, size=16, color="grey"), ft.Text(f"{a.get('discipline')} - {a.get('enseignement')}", color="grey")]),
            ft.Divider(height=30),
            ft.Text("Descriptif Pedagogique :", weight="bold", size=16),
            ft.Markdown(desc, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB),
            ft.Divider(height=20),
            ft.Row([
                ft.Column([
                    ft.Text("Prerequis techniques :", weight="bold"),
                    ft.Row([ft.Chip(label=ft.Text(f"#{p}")) for p in a.get("prerequis_ids", [])], wrap=True) if a.get("prerequis_ids") else ft.Text("Aucun", size=12, italic=True)
                ], expand=True),
                ft.Column([
                    ft.Text("Sous-competences (Enfants) :", weight="bold"),
                    ft.Row([ft.Chip(label=ft.Text(f"#{c}"), bgcolor="#F3E5F5") for c in a.get("enfants_ids", [])], wrap=True) if a.get("enfants_ids") else ft.Text("Structure atomique", size=12, italic=True)
                ], expand=True),
            ]),
            ft.Divider(height=10, color="transparent"),
            ft.Row([
                ft.ElevatedButton("Analyse Graphique de l'Ontologie", icon=ft.Icons.GRAPHIC_EQ, on_click=lambda _: self.show_graph(a), bgcolor="#546E7A", color="white", expand=True),
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], scroll=ft.ScrollMode.AUTO)
        
        self._set_detail(content)

    def show_graph(self, aav):
        """Gere la generation dynamique du graphe de dependances via NetworkX et Matplotlib."""
        matplotlib.use('Agg')
        G = nx.DiGraph()
        curr_id = aav["id_aav"]
        curr_name = aav.get("nom", f"AAV #{curr_id}")
        
        def get_label(id_val):
            for item in self.all_aavs:
                if str(item.get("id_aav")) == str(id_val): return item.get("nom", f"#{id_val}")
            return f"ID {id_val}"

        def extract_list(data):
            if not data: return []
            if isinstance(data, list): return data
            if isinstance(data, str):
                try: return json.loads(data)
                except: return [data]
            return []

        prereqs = extract_list(aav.get("prerequis_ids"))
        children = extract_list(aav.get("aav_enfant_ponderation") or aav.get("enfants_ids"))

        G.add_node(curr_name, color="#E64A19")
        for p_id in prereqs:
            p_label = get_label(p_id); G.add_node(p_label, color="#1976D2"); G.add_edge(p_label, curr_name)
        for c_id in children:
            c_label = get_label(c_id); G.add_node(c_label, color="#388E3C"); G.add_edge(curr_name, c_label)

        fig = Figure(figsize=(8, 6), facecolor='#F5F7FA')
        ax = fig.add_subplot(111); ax.set_axis_off()

        if len(G.nodes) > 1:
            pos = nx.spring_layout(G, k=0.8, iterations=50)
            colors = [nx.get_node_attributes(G, 'color').get(node, "#90A4AE") for node in G.nodes()]
            nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors, node_size=2500, alpha=0.9)
            nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_weight="bold")
            nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#455A64", arrows=True)
        else:
            ax.text(0.5, 0.5, "Structure isolee.", ha='center', va='center')

        ax.set_title(f"Visualisation Ontologique : {curr_name}", size=14, weight="bold")

        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        chart = ft.Image(src=f"data:image/png;base64,{img_b64}", expand=True, fit=ft.BoxFit.CONTAIN)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Exploration de l'Ontologie"),
            content=ft.Container(content=chart, width=800, height=600),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or self._page.update())]
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def build(self, page: ft.Page):
        """Construit l'interface globale de la page referentiel."""
        self._page = page
        self.load_data()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.Icons.ARCHITECTURE, color="white", size=30), bgcolor="#1565C0", padding=10, border_radius=10),
                    ft.Text("Referentiel des Competences (AAV)", size=26, weight="bold", color="#1565C0"),
                ]),
                ft.Row([
                    self.search_field, self.discipline_filter, self.type_filter,
                    ft.IconButton(ft.Icons.REFRESH, on_click=self.load_data),
                    ft.ElevatedButton("Nouvel AAV", icon=ft.Icons.ADD, on_click=self.ouvrir_creation, bgcolor="#43A047", color="white", visible=self.is_professor)
                ], spacing=10),
                ft.Row([
                    ft.Container(content=self.list_view, width=400, border=ft.border.all(1, "#E3F2FD"), border_radius=12, bgcolor="#FAFAFA"),
                    self.detail_container
                ], expand=True, spacing=20)
            ], spacing=20),
            padding=30, expand=True
        )

    def ouvrir_creation(self, e):
        """
        Ouvre le formulaire de creation d'un nouvel AAV.

        Valide les donnees saisies en utilisant le schema Pydantic AAVCreate
        avant tout envoi a l'API. Gere egalement la liaison parent/enfant
        via le champ aav_enfant_ponderation pour les AAV de type Composite.
        """
        selected_prereqs, selected_children = [], []
        champ_id = ft.TextField(label="Identifiant Unique", keyboard_type=ft.KeyboardType.NUMBER)
        champ_nom = ft.TextField(label="Intitule de la competence")
        champ_libelle = ft.TextField(label="Libelle d'integration")
        champ_disc = ft.TextField(label="Domaine disciplinaire")
        champ_ens = ft.TextField(label="Enseignement")
        champ_desc = ft.TextField(label="Description technique (Markdown)", multiline=True, min_lines=3)
        champ_type = ft.SegmentedButton(
            selected=["Atomique"],
            segments=[ft.Segment(value="Atomique", label=ft.Text("Atomique")), ft.Segment(value="Composite (Chapitre)", label=ft.Text("Composite"))]
        )
        champ_eval = ft.Dropdown(
            label="Type d'evaluation",
            options=[ft.dropdown.Option(x.value) for x in TypeEvaluationAAV],
            value=TypeEvaluationAAV.HUMAINE.value
        )
        err_text = ft.Text("", color="red", visible=False)

        def get_all_ids_options():
            """Retourne les options Dropdown a partir des AAV charges en memoire."""
            return [ft.dropdown.Option(str(a["id_aav"]), f"#{a['id_aav']} {a['nom']}") for a in self.all_aavs]

        drop_prereq = ft.Dropdown(label="Prerequis", options=get_all_ids_options(), width=250)
        drop_child = ft.Dropdown(label="Dependances", options=get_all_ids_options(), width=250)
        chip_row_p, chip_row_c = ft.Row(wrap=True), ft.Row(wrap=True)

        def add_id(dropdown, selected_list, chip_row):
            """Ajoute un identifiant AAV a la liste de selection et affiche un chip."""
            if dropdown.value and dropdown.value not in selected_list:
                selected_list.append(dropdown.value)
                chip_row.controls.append(ft.Chip(label=ft.Text(f"#{dropdown.value}"), on_delete=lambda e, val=dropdown.value: remove_id(val, selected_list, chip_row)))
                self._page.update()

        def remove_id(val, selected_list, chip_row):
            """Retire un identifiant AAV de la liste de selection et supprime son chip."""
            selected_list.remove(val)
            chip_row.controls = [c for c in chip_row.controls if c.label.value != f"#{val}"]
            self._page.update()

        def valider(ev):
            """
            Valide les donnees du formulaire via Pydantic puis soumet a l'API.

            Leve une ValidationError si les champs requis sont invalides ou manquants.
            Les erreurs sont affichees directement dans la vue sans fermer le dialogue.
            """
            is_composite = "Composite" in champ_type.selected
            try:
                aav_create = AAVCreate(
                    id_aav=int(champ_id.value) if champ_id.value else -1,
                    nom=champ_nom.value or "",
                    libelle_integration=champ_libelle.value or "",
                    discipline=champ_disc.value or "",
                    enseignement=champ_ens.value or "",
                    description_markdown=champ_desc.value or "",
                    type_aav=champ_type.selected[0] if champ_type.selected else "Atomique",
                    type_evaluation=champ_eval.value,
                    prerequis_ids=[int(i) for i in selected_prereqs],
                    regles_progression=RegleProgression()
                )
                payload = aav_create.model_dump()
                if is_composite:
                    payload["aav_enfant_ponderation"] = [int(i) for i in selected_children]
                r = httpx.post(f"{BASE_URL}/aavs/", json=payload)
                if r.status_code in [200, 201]:
                    dialog.open = False
                    self.load_data()
                else:
                    err_text.value = f"Erreur Serveur: {r.text}"
                    err_text.visible = True
                self._page.update()
            except ValidationError as ve:
                err_text.value = f"Erreur de validation : {ve.errors()[0]['msg']} (champ : {ve.errors()[0]['loc'][0]})"
                err_text.visible = True
                self._page.update()
            except ValueError:
                err_text.value = "Format de nombre invalide pour l'identifiant AAV."
                err_text.visible = True
                self._page.update()
            except Exception as ex:
                err_text.value = f"Erreur inattendue : {str(ex)}"
                err_text.visible = True
                self._page.update()

        btn_add_p = ft.IconButton(ft.Icons.ADD, on_click=lambda _: add_id(drop_prereq, selected_prereqs, chip_row_p))
        btn_add_c = ft.IconButton(ft.Icons.ADD, on_click=lambda _: add_id(drop_child, selected_children, chip_row_c))

        dialog = ft.AlertDialog(
            title=ft.Text("Definition Technique AAV"),
            content=ft.Container(
                content=ft.Column([
                    err_text,
                    ft.Row([champ_id, champ_nom]),
                    ft.Row([champ_libelle, champ_desc], vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Row([champ_disc, champ_ens]),
                    ft.Text("Architecture et Evaluation:", weight="bold"),
                    ft.Row([champ_type, champ_eval]),
                    ft.Row([drop_prereq, btn_add_p]), chip_row_p,
                    ft.Row([drop_child, btn_add_c]), chip_row_c,
                ], scroll=ft.ScrollMode.AUTO, spacing=15),
                width=650, height=700
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Enregistrer", bgcolor="#43A047", color="white", on_click=valider)
            ]
        )
        self._page.overlay.append(dialog); dialog.open = True; self._page.update()

