import sys
from pathlib import Path

# Add project root (projet_python) to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../projet_python
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft
from pages import AlertsPage, DetailsPage, Sidebar, AboutPage


def main(page: ft.Page):
    """
    Main application entry point for the AAV Dashboard GUI.
    
    Sets up the Flet application with theme configuration, window properties,
    and initializes the navigation system between AlertsPage and DetailsPage.
    Manages the content_area container that switches between pages on user interaction.
    
    Architecture:
    - content_area (ft.Column): Main container that holds either alerts or details view
    - show_alerts(e=None): Callback to display the alerts dashboard
    - show_details(aav_id): Callback to display details for a specific AAV
    - AlertsPage: Instantiated on alerts view with show_details callback
    - DetailsPage: Instantiated on details view with show_alerts callback
    
    Args:
        page (ft.Page): The root Flet page object provided by ft.app()
    
    Returns:
        None (modifies page in-place)
    
    Side Effects:
        - Configures page title, theme, window size, colors, and padding
        - Adds content_area column to page
        - Initializes with alerts dashboard displayed
    
    UI Features:
        - Dark theme with purple accent color scheme
        - Window size: 900x700 pixels
        - Auto-scrolling content area
        - Multi-page navigation via AlertsPage and DetailsPage classes
    """
    page.title = "AAV Dashboard"
    page.bgcolor = "#1a1a2e"
    page.theme = ft.Theme(color_scheme_seed="#9C27B0")
    page.window.width = 900
    page.window.height = 700
    page.padding = 0

    # ===== CONTENT AREA (for navigation) =====
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    # ===== PAGE INSTANCES =====
    def show_alerts(e=None):
        """
        Navigate to the alerts dashboard page.
        
        Clears the content area, instantiates a new AlertsPage object,
        builds the alerts UI, and displays it. Called on app startup and
        when user clicks "Back to Alerts" button.
        
        Args:
            e (ft.ControlEvent, optional): Event object from button click. Defaults to None.
        
        Returns:
            None
        
        Side Effects:
            - Clears content_area controls
            - Creates new AlertsPage instance
            - Adds alerts UI to content_area
            - Updates page display
        """
        content_area.controls.clear()
        alerts_page = AlertsPage(content_area, show_details, show_about)
        alerts_content = alerts_page.build(page)
        content_area.controls.append(alerts_content)
        page.update()
    
    def show_details(aav_id):
        """
        Navigate to the AAV details page for a specific AAV.
        
        Clears the content area, instantiates a new DetailsPage object,
        builds the details UI for the given AAV ID, and displays it.
        Called when user clicks on an AAV row in the alerts dashboard.
        
        Args:
            aav_id (int or str): Unique identifier of the AAV to display
        
        Returns:
            None
        
        Side Effects:
            - Clears content_area controls
            - Creates new DetailsPage instance
            - Fetches AAV data from API
            - Adds details UI to content_area
            - Updates page display
        """
        content_area.controls.clear()
        details_page = DetailsPage(content_area, show_about)
        details_content = details_page.build(aav_id, page)
        content_area.controls.append(details_content)
        page.update()
    
    def show_about(e=None):
        """
        Navigate to the about/project information page.
        
        Clears the content area, instantiates a new AboutPage object,
        builds the about UI, and displays it. Called when user clicks
        "About" button in the sidebar.
        
        Args:
            e (ft.ControlEvent, optional): Event object from button click. Defaults to None.
        
        Returns:
            None
        
        Side Effects:
            - Clears content_area controls
            - Creates new AboutPage instance
            - Adds about UI to content_area
            - Updates page display
        """
        content_area.controls.clear()
        about_page = AboutPage(content_area, show_alerts)
        about_content = about_page.build(page)
        content_area.controls.append(about_content)
        page.update()
    
    # ===== SIDEBAR =====
    sidebar = Sidebar(show_alerts, show_about)
    sidebar_ui = sidebar.build()
    
    # Main layout: Row with sidebar on left and content on right
    main_layout = ft.Row(
        [
            ft.Container(
                content=sidebar_ui,
                width=260,
                height=700,
                expand=False,
                bgcolor="#22223e",
                alignment=ft.alignment.top_left,
            ),
            ft.VerticalDivider(width=1, color="#424242"),
            content_area,
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
    
    show_about()
    
    page.add(main_layout)


if __name__ == "__main__":
    ft.app(main)