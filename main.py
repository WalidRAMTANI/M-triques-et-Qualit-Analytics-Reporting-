import flet as ft

# On importe la vue AAV que l'on vient de créer
from flet_app.aav.aav_view import create_aav_view

def main(page: ft.Page):
    page.title = "Application Flet - Météodes et Qualité"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_200
    
    # On ajoute directement le composant AAV à notre page principale.
    # C'est comme ça qu'on fait le lien entre __main__ et le dossier aav !
    page.add(create_aav_view(page))

if __name__ == "__main__":
    ft.app(main)
