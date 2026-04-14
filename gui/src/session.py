"""
Session view — consomme l'API REST via HTTP (httpx).
Endpoints : /sessions/, /sessions/{id}, /attempts
Retourne un Container (ne fait PAS page.add()).
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft
import httpx

BASE_URL = "http://localhost:8000"


def _get(path: str):
    try:
        r = httpx.get(f"{BASE_URL}{path}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"[GET] {path} → {e}")
        return None


def _post(path: str, payload: dict = None):
    try:
        r = httpx.post(f"{BASE_URL}{path}", json=payload or {}, timeout=10)
        return (r.json(), r.status_code)
    except Exception as e:
        print(f"[POST] {path} → {e}")
        return (None, 500)


def _put(path: str, payload: dict = None):
    try:
        r = httpx.put(f"{BASE_URL}{path}", json=payload or {}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"[PUT] {path} → {e}")
        return None


def _delete(path: str):
    try:
        r = httpx.delete(f"{BASE_URL}{path}", timeout=5)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"[DELETE] {path} → {e}")
        return False


def build_session_view(page: ft.Page):
    """Retourne un ft.Container (sans appeler page.add())."""

    champ_chiffre = ft.TextField(
        label="Numéro Session",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        border_color="#9C27B0",
        bgcolor="#F3E5F5",
        prefix_icon=ft.Icons.SEARCH,
        cursor_color="#7B1FA2",
    )

    affichage_resultat = ft.Text("Résultat : aucun", size=18, color="#7B1FA2")

    bouton_modifier = ft.ElevatedButton(
        "Modifier état",
        visible=False,
        on_click=lambda e: ouvrir_popup_modifier(e)
    )

    bouton_supprimer = ft.ElevatedButton(
        "Supprimer",
        visible=False,
        on_click=lambda e: action_supprimer(e),
        color="#FFFFFF",
        bgcolor="#F44336"
    )

    bouton_simuler = ft.ElevatedButton(
        "Simuler Tentative",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        visible=False,
        on_click=lambda e: ouvrir_popup_simulation(e),
        bgcolor=ft.Colors.ORANGE_700,
        color=ft.Colors.WHITE
    )

    boite_fixe = ft.Container(
        content=ft.Column([affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
        width=600,
        height=400,
        bgcolor="#FFFFFF",
        border_radius=10,
        padding=16,
        border=ft.border.all(1, "#E1BEE7")
    )

    # Stockage des données de session courante
    _current = {"apprenant_id": None, "activite_id": None}

    def donnee_session(e):
        if not champ_chiffre.value:
            return

        res = _get(f"/sessions/{champ_chiffre.value}")
        if res and "id_session" in res:
            affichage_resultat.value = (
                f"Session ID: {res.get('id_session')}\n"
                f"ID Activité: {res.get('id_activite')}\n"
                f"ID Apprenant: {res.get('id_apprenant')}\n"
                f"Statut: {str(res.get('statut', '')).upper()}\n"
                f"Date Début: {res.get('date_debut')}\n"
                f"Date Fin: {res.get('date_fin')}\n"
                f"Bilan: {res.get('bilan')}\n"
            )
            affichage_resultat.color = "#212121"
            bouton_modifier.visible = True
            bouton_supprimer.visible = True
            bouton_simuler.visible = True
            _current["apprenant_id"] = res.get("id_apprenant")
            _current["activite_id"] = res.get("id_activite")
        else:
            affichage_resultat.value = "Aucune session ne correspond à ce numéro"
            affichage_resultat.color = "#F44336"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            bouton_simuler.visible = False

        page.update()

    def ouvrir_popup_creation(e):
        champ_activite = ft.TextField(label="ID Activité", keyboard_type=ft.KeyboardType.NUMBER)
        champ_apprenant = ft.TextField(label="ID Apprenant", keyboard_type=ft.KeyboardType.NUMBER)

        def valider_creation(ev):
            if not champ_activite.value or not champ_apprenant.value:
                return
            donnees = {
                "id_activite": int(champ_activite.value),
                "id_apprenant": int(champ_apprenant.value)
            }
            res, code = _post("/sessions/", donnees)
            dialog.open = False
            if res and res.get("id_session"):
                champ_chiffre.value = str(res["id_session"])
                page.update()
                donnee_session(None)
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erreur création session (code {code})"))
                page.snack_bar.open = True
                page.update()

        def annuler(ev):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Créer une nouvelle session"),
            content=ft.Column([champ_activite, champ_apprenant], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=annuler),
                ft.ElevatedButton("Créer", on_click=valider_creation, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE)
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def ouvrir_popup_modifier(e):
        if not champ_chiffre.value:
            return
        id_actuel = int(champ_chiffre.value)
        res = _get(f"/sessions/{id_actuel}")
        if not res:
            return

        def changer_statut(nouveau_statut):
            if nouveau_statut == "started":
                _put(f"/sessions/{id_actuel}/start")
            elif nouveau_statut == "closed":
                _put(f"/sessions/{id_actuel}/close")
            dialog.open = False
            page.update()
            donnee_session(None)

        dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier Session n°{id_actuel}"),
            content=ft.Text(f"Statut actuel : {res.get('statut', '?')}"),
            actions=[
                ft.ElevatedButton("Démarrer", on_click=lambda _: changer_statut("started"), bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE),
                ft.ElevatedButton("Clôturer", on_click=lambda _: changer_statut("closed"), bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE),
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or page.update())
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def ouvrir_popup_toutes_sessions(e):
        res = _get("/sessions/")
        liste_sessions = res.get("sessions", []) if res else []

        def charger_session(id_s):
            champ_chiffre.value = str(id_s)
            dialog.open = False
            page.update()
            donnee_session(None)

        items_list = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, color=ft.Colors.PURPLE_400),
                title=ft.Text(f"Session {s['id_session']} (Apprenant: {s['id_apprenant']})", weight="bold"),
                subtitle=ft.Text(f"Activité: {s['id_activite']} | Statut: {s['statut']}"),
                on_click=lambda e, id_v=s['id_session']: charger_session(id_v)
            )
            for s in liste_sessions
        ] or [ft.Text("Aucune session.", italic=True)]

        dialog = ft.AlertDialog(
            title=ft.Text("Liste de toutes les Sessions"),
            content=ft.Container(
                content=ft.ListView(items_list, spacing=10, padding=10),
                width=500,
                height=400,
            ),
            actions=[ft.TextButton("Fermer", on_click=lambda _: setattr(dialog, "open", False) or page.update())]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def ouvrir_popup_simulation(e):
        champ_aav = ft.TextField(label="ID AAV Cible", keyboard_type=ft.KeyboardType.NUMBER)
        champ_exercice = ft.TextField(label="ID Exercice", keyboard_type=ft.KeyboardType.NUMBER)
        champ_score = ft.TextField(label="Score Obtenu (0.0 - 1.0)", keyboard_type=ft.KeyboardType.NUMBER)
        champ_valide = ft.Checkbox(label="Tentative Valide", value=True)

        def valider_simulation(ev):
            if not champ_aav.value or not champ_score.value:
                return
            payload = {
                "id_exercice_ou_evenement": int(champ_exercice.value or 0),
                "id_apprenant": _current["apprenant_id"],
                "id_aav_cible": int(champ_aav.value),
                "date_tentative": datetime.now().isoformat(),
                "score_obtenu": float(champ_score.value),
                "est_valide": champ_valide.value,
                "meta_data": {}
            }
            res, code = _post("/attempts", payload)
            dialog.open = False
            if code == 201:
                page.snack_bar = ft.SnackBar(ft.Text("✅ Tentative simulée avec succès !"))
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ Erreur lors de l'envoi (code {code})"))
            page.snack_bar.open = True
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Simuler une Tentative d'Apprenant"),
            content=ft.Column([
                ft.Text(f"Apprenant ID: {_current['apprenant_id']}"),
                champ_aav, champ_exercice, champ_score, champ_valide
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or page.update()),
                ft.ElevatedButton("Envoyer Score", on_click=valider_simulation, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE)
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def action_supprimer(e):
        if not champ_chiffre.value:
            return
        id_actuel = int(champ_chiffre.value)
        ok = _delete(f"/sessions/{id_actuel}")
        if ok:
            affichage_resultat.value = "✅ Session supprimée avec succès."
            affichage_resultat.color = "#4CAF50"
            bouton_modifier.visible = False
            bouton_supprimer.visible = False
            bouton_simuler.visible = False
        else:
            affichage_resultat.value = "❌ Erreur lors de la suppression."
            affichage_resultat.color = "#F44336"
        page.update()

    # ── Layout (retourné, pas ajouté à page) ──────────────────────────────────
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Gestion des Sessions", size=28, weight="bold", color="#7B1FA2"),
                ft.Divider(height=20, color="transparent"),
                champ_chiffre,
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    ft.ElevatedButton("Rechercher", on_click=donnee_session, icon=ft.Icons.SEARCH),
                    ft.ElevatedButton("Nouvelle Session", on_click=ouvrir_popup_creation, icon=ft.Icons.ADD, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Liste des Sessions", on_click=ouvrir_popup_toutes_sessions, icon=ft.Icons.LIST, bgcolor=ft.Colors.PURPLE_400, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=15, color="transparent"),
                boite_fixe,
                ft.Divider(height=15, color="transparent"),
                ft.Row([bouton_modifier, bouton_supprimer, bouton_simuler], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor="#FFFFFF",
        expand=True,
        padding=20,
    )


def main(page: ft.Page):
    """Standalone entry point."""
    page.title = "Gestion des Sessions"
    page.bgcolor = "#F5F5F5"
    page.add(build_session_view(page))


if __name__ == "__main__":
    ft.app(target=main)
