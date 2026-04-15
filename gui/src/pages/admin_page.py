import flet as ft

class AdminPage:
    """
    Page d'administration et d'authentification.
    Permet de basculer entre le mode Apprenant (lecture seule) et le mode Professeur (edition).
    """

    def __init__(self, content_area, on_login_success, on_logout, is_professor=False):
        """Initialise les references de session et les composants de saisie."""
        self.content_area = content_area
        self.on_login_success = on_login_success
        self.on_logout = on_logout
        self.is_professor = is_professor
        self.password_field = ft.TextField(
            label="Code Administrateur",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=self.check_login
        )
        self.status_text = ft.Text("", color="red")

    def check_login(self, e):
        """Verifie la validite des identifiants et decline les acces non autorises."""
        if self.password_field.value == "admin":
            self.on_login_success()
        else:
            self.status_text.value = "Code de securite incorrect."
            self.status_text.update()

    def build(self, page: ft.Page):
        """Construit l'interface de connexion ou de deconnexion selon l'etat de session."""
        if self.is_professor:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LOCK_OPEN, size=60, color="green"),
                    ft.Text("Session Professeur Active", size=24, weight="bold"),
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton("Se deconnecter (Mode Eleve)", on_click=lambda _: self.on_logout(), bgcolor="#F44336", color="white", width=300),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                expand=True, alignment=ft.Alignment(0, 0)
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCK_PERSON, size=60, color="#1565C0"),
                ft.Text("Connexion Professeur", size=24, weight="bold"),
                ft.Text("Veuillez saisir le code d'acces pour debloquer les privileges d'edition.", color="grey"),
                ft.Divider(height=20, color="transparent"),
                self.password_field,
                ft.ElevatedButton("Authentification", on_click=self.check_login, bgcolor="#1565C0", color="white", width=300),
                self.status_text,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            expand=True, alignment=ft.Alignment(0, 0)
        )
