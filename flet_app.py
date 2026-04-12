import flet as ft

def main(page: ft.Page):
    page.title = "Maquette Inspiree du Design"
    # Supprimer les marges par défaut pour que les conteneurs prennent tout l'espace
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Couleurs extraites du design
    blue_color = "#7A98BB"  # Bleu/Gris de la barre et du menu
    cyan_color = "#C8F6F4"  # Cyan clair du contenu principal
    
    # État du menu latéral
    sidebar_visible = True
    
    def toggle_sidebar(e):
        nonlocal sidebar_visible
        sidebar_visible = not sidebar_visible
        
        # Mettre à jour la visibilité 
        sidebar.visible = sidebar_visible
        top_menu_btn.visible = not sidebar_visible
        
        # Changer le contenu principal selon que l'on soit sur la vue 1 (gauche) ou 2 (droite) du mock-up
        if sidebar_visible:
            main_content.content = content_view_1
        else:
            main_content.content = content_view_2
            
        # Rafraîchir l'interface
        page.update()

    # --- ÉLÉMENTS DE MENU ---
    # Bouton Menu dans la barre latérale
    side_menu_btn = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.MENU, 
            icon_color="black",
            icon_size=30,
            on_click=toggle_sidebar
        ),
        alignment=ft.alignment.top_left,
        padding=5
    )
    
    # Bouton Menu dans la barre du haut (visible quand sidebar est fermée)
    top_menu_btn = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.MENU, 
            icon_color="black",
            icon_size=30,
            on_click=toggle_sidebar
        ),
        visible=not sidebar_visible, # initialement caché
        padding=5
    )

    # --- SECTIONS DE LA FENÊTRE ---
    # Barre latérale (Sidebar) à gauche
    sidebar = ft.Container(
        width=250,
        bgcolor=blue_color,
        # Bordures noires épaisses comme sur l'image
        border=ft.border.only(
            right=ft.border.BorderSide(3, "black"),
        ),
        content=ft.Column([
            side_menu_btn,
            # On peut ajouter ici d'autres boutons pour la navigation
        ]),
        visible=sidebar_visible
    )

    # Barre du haut (Top Bar)
    top_bar = ft.Container(
        height=70,
        bgcolor=blue_color,
        border=ft.border.only(
            bottom=ft.border.BorderSide(3, "black")
        ),
        content=ft.Row([
            top_menu_btn,
        ], alignment=ft.MainAxisAlignment.START)
    )
    
    # --- CONTENUS MOCK-UP ---
    # Vue correspondant à l'image de GAUCHE (Texte : "Présentation du projet")
    content_view_1 = ft.Column(
        [
            ft.Text("Présentation du\nprojet", size=48, color="black")
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    # Vue correspondant à l'image de DROITE (Bouton encadré : "Présentation")
    content_view_2 = ft.Container(
        content=ft.Text("Présentation", size=32, color="black"),
        # Simulation du bouton aux bords arrondis avec la même couleur de fond
        bgcolor=cyan_color,
        border=ft.border.all(3, "#7A98BB"),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=40, vertical=15)
    )

    # Zone de contenu principal
    main_content = ft.Container(
        expand=True,
        bgcolor=cyan_color,
        alignment=ft.alignment.center,
        content=content_view_1
    )
    
    # La colonne de droite contient la barre du haut et le contenu
    right_pane = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            top_bar,
            main_content
        ]
    )
    
    # Ajout du Layout principal (Row) regroupant la Sidebar et le panneau de droite
    page.add(
        ft.Row(
            spacing=0,
            expand=True,
            controls=[
                sidebar,
                right_pane
            ]
        )
    )

if __name__ == "__main__":
    # Ouvre l'app dans une fenêtre native.
    ft.app(target=main)
