"""
Utility functions for AAV Dashboard GUI.

Contains:
- API fetch function
- UI helper functions (row, section)
- API constants
"""

import flet as ft
import httpx

ALERTS_API = "http://localhost:8000/alerts"
AAVS_API = "http://localhost:8000/aavs"
METRIQUE_API = "http://localhost:8000/metriques"
SESSION_API = "http://localhost:8000/sessions"

def fetch(path, base_api=ALERTS_API):
    """
    Fetch data from a RESTful API endpoint with error handling.
    
    Makes an HTTP GET request to the specified API endpoint and returns
    the JSON response. Implements a 5-second timeout and gracefully handles
    connection errors, timeouts, and HTTP errors.
    
    Args:
        path (str): API endpoint path (e.g., "/difficult-aavs", "/students-at-risk/123")
        base_api (str, optional): Base API URL. Defaults to ALERTS_API.
            Use AAVS_API for AAV-specific endpoints.
    
    Returns:
        list or dict: Parsed JSON response from the API, or empty list [] on failure
    
    Raises:
        No exceptions raised; returns [] on any error (connection, timeout, HTTP errors)
    
    Example:
        >>> difficult_aavs = fetch("/difficult-aavs", ALERTS_API)
        >>> aav_details = fetch("/123", AAVS_API)
    """
    try:
        r = httpx.get(f"{base_api}{path}", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def row(left, right, color="#FFFFFF"):
    """
    Create a labeled row UI component with two text columns.
    
    Constructs a horizontal Flet Row with a left column (label) and right column (value).
    The left column uses 70% opacity white text and is expandable, while the right
    column displays the value in the specified color with bold font weight.
    
    Args:
        left (str): Left column text (typically a label). Expands to fill available space.
        right (str or int or float): Right column text (typically a value).
            Automatically converted to string.
        color (str, optional): Flet color constant for right column text.
            Defaults to white (#FFFFFF). Common values: #FF5252, #4CAF50, #FF9800
    
    Returns:
        ft.Row: Horizontal row control with two text columns
    
    Example:
        >>> row("Status", "Active", "#4CAF50")
        >>> row("Progression", "75%", "#2196F3")
    """
    return ft.Row([
        ft.Text(left, expand=True, color="#E0E0E0"),
        ft.Text(right, color=color, weight=ft.FontWeight.W_500),
    ])


def section(title, items):
    """
    Create a styled section container with title and content items.
    
    Constructs a reusable section component with a semi-transparent background,
    rounded corners, and padding. Each section includes a title header with divider
    and a list of content items. If no items are provided, displays a placeholder
    "No results" message in dimmed text.
    
    Args:
        title (str): Section heading text, displayed in white with font size 16
        items (list of ft.Control or empty list): List of Flet UI controls to display
            below the title. Common items: ft.Row, ft.Container, ft.Text.
            Pass empty list [] to show "No results" message.
    
    Returns:
        ft.Container: Styled container with background color #2a2a3e (WHITE10),
            border radius 10px, and 16px padding. Contains vertically-stacked title,
            divider, and content items.
    
    Example:
        >>> items = [row("Nom", "Calcul"), row("Type", "Exercise")]
        >>> section("AAV Information", items)
        
        >>> section("Empty Section", [])  # Shows "Aucun résultat."
    """
    content_list = [
        ft.Text(title, size=16, weight=ft.FontWeight.W_500),
        ft.Divider(height=1),
    ]
    if items:
        content_list.extend(items)
    else:
        content_list.append(ft.Text("Aucun résultat.", color=ft.Colors.WHITE38))
    
    return ft.Container(
        content=ft.Column(content_list),
        bgcolor=ft.Colors.WHITE10,
        border_radius=10,
        padding=16,
    )
