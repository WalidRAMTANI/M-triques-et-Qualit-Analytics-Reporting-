"""
Utilitaires de support pour l'interface graphique AAV Dashboard.

Regroupe les fonctions de communication avec l'API REST, les aides a la
construction de composants UI standardises et les constantes de configuration.
"""

import flet as ft
import httpx

# Definitions des points de terminaison de reference
ALERTS_API = "http://localhost:8000/alerts"
AAV_API = "http://localhost:8000/aavs"
METRIQUES_API = "http://localhost:8000/metriques"
SESSIONS_API = "http://localhost:8000/sessions"

def fetch(path, base_api=ALERTS_API):
    """
    Effectue une requete GET securisee vers un point de terminaison API.
    
    Gere les delais d'attente (timeout) et les erreurs de connectivite
    en retournant une structure vide en cas d'echec.
    
    Args:
        path (str): Chemin relatif du critere de recherche.
        base_api (str, optional): Racine de l'API cible. Par defaut: ALERTS_API.
    
    Returns:
        list|dict: Donnees JSON decodees ou liste vide en cas d'anomalie.
    """
    try:
        r = httpx.get(f"{base_api}{path}", timeout=10)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def row(left, right, color="#FFFFFF"):
    """
    Genere un composant de ligne informatif bi-colonne.
    
    Structure une etiquette (label) a gauche et sa valeur associee a droite
    avec une mise en forme typographique distincte.
    
    Args:
        left (str): Libelle de l'information (etiquette).
        right (any): Valeur ou contenu textuel a afficher.
        color (str, optional): Code couleur hexadesimal pour la valeur.
    
    Returns:
        ft.Row: Un composant horizontal Flet structure.
    """
    return ft.Row([
        ft.Text(str(left), expand=True, color="#E0E0E0", size=13),
        ft.Text(str(right), color=color, weight=ft.FontWeight.W_500, selectable=True),
    ])

def section(title, items):
    """
    Construit un bloc de section structure avec une entête et un corps de contenu.
    
    Encapsule une serie de contrôles dans un conteneur visuel coherent avec
    une separation claire et une gestion des etats vides.
    
    Args:
        title (str): Titre de la section (entête).
        items (list): Liste de composants ft.Control a inserer dans le corps.
    
    Returns:
        ft.Container: Un bloc visuel standardise avec une esthetique premium.
    """
    content_list = [
        ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="#CE93D8"),
        ft.Divider(height=2, color="#424242"),
    ]
    if items:
        content_list.extend(items)
    else:
        content_list.append(ft.Text("Aucune donnee disponible.", color="#757575", italic=True))
    
    return ft.Container(
        content=ft.Column(content_list, spacing=12),
        bgcolor="#2a2a3e",
        border_radius=12,
        padding=20,
        margin=ft.margin.only(bottom=15)
    )
