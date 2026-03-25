#!/usr/bin/env python3
"""
Programme de vérification pour le Groupe 4 - Activités Pédagogiques.

Ce script teste:
- PARTIE COMMUNE: Connexion, CRUD de base
- PARTIE SPECIFIQUE: Gestion des activités et sessions

Usage:
    python test_groupe4.py
    python test_groupe4.py --url http://localhost:8000
"""

import argparse
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    import urllib.request
    import urllib.error
    import json


class TestStatus(Enum):
    """Statut d'un test."""
    PASSED = "✅ PASS"
    FAILED = "❌ FAIL"
    SKIPPED = "⏭️  SKIP"
    ERROR = "💥 ERR"


@dataclass
class TestResult:
    """Résultat d'un test."""
    name: str
    status: TestStatus
    message: str = ""
    details: Optional[Dict] = None


class BaseTester:
    """Classe de base pour les tests."""

    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.client = None

        if HAS_HTTPX:
            self.client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def log(self, message: str, level: str = "info"):
        """Affiche un message si verbose est activé."""
        if self.verbose or level in ["error", "success"]:
            prefix = {
                "info": "ℹ️  ",
                "success": "✅ ",
                "error": "❌ ",
                "warning": "⚠️  ",
                "test": "🧪 "
            }.get(level, "")
            print(f"{prefix}{message}")

    def _request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """Effectue une requête HTTP."""
        url = f"{self.base_url}{endpoint}"
        try:
            if HAS_HTTPX and self.client:
                response = self.client.request(method, endpoint, **kwargs)
                return response.status_code, response.json() if response.content else None, None
            else:
                req = urllib.request.Request(
                    url,
                    data=kwargs.get('json', {}).encode() if 'json' in kwargs else None,
                    headers={'Content-Type': 'application/json'} if 'json' in kwargs else {},
                    method=method
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    status = response.status
                    data = json.loads(response.read().decode()) if response.read() else None
                    return status, data, None
        except Exception as e:
            return None, None, str(e)

    def add_result(self, name: str, status: TestStatus, message: str = "", details: Optional[Dict] = None):
        """Ajoute un résultat de test."""
        self.results.append(TestResult(name=name, status=status, message=message, details=details))

    # =============================================================================
    # PARTIE COMMUNE - Tests de base
    # =============================================================================

    def test_health_check(self):
        """Teste le endpoint /health."""
        self.log("Test: Health check", "test")
        status, data, error = self._request("GET", "/health")
        if error:
            self.add_result("Health Check", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data and data.get("status") == "healthy":
            self.add_result("Health Check", TestStatus.PASSED, "Serveur opérationnel")
            return True
        else:
            self.add_result("Health Check", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_root_endpoint(self):
        """Teste le endpoint /."""
        self.log("Test: Root endpoint", "test")
        status, data, error = self._request("GET", "/")
        if error:
            self.add_result("Root Endpoint", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data and "PlatonAAV" in data.get("message", ""):
            self.add_result("Root Endpoint", TestStatus.PASSED, "API accessible")
            return True
        else:
            self.add_result("Root Endpoint", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_list_aavs(self):
        """Teste GET /aavs/."""
        self.log("Test: Liste des AAV", "test")
        status, data, error = self._request("GET", "/aavs/")
        if error:
            self.add_result("List AAVs", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and isinstance(data, list):
            self.add_result("List AAVs", TestStatus.PASSED, f"{len(data)} AAV récupérés")
            return True
        else:
            self.add_result("List AAVs", TestStatus.FAILED, f"Status: {status}")
            return False

    # =============================================================================
    # PARTIE SPECIFIQUE AU GROUPE 4
    # =============================================================================

    def test_list_activites(self):
        """Teste GET /activites/."""
        self.log("Test: Liste des activités", "test")
        status, data, error = self._request("GET", "/activites/")
        if error:
            self.add_result("List Activités", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and isinstance(data, list):
            self.add_result("List Activités", TestStatus.PASSED, f"{len(data)} activités")
            return True
        elif status == 404:
            self.add_result("List Activités", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 4)")
            return True
        else:
            self.add_result("List Activités", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_create_activite(self):
        """Teste POST /activites/."""
        self.log("Test: Création d'une activité", "test")
        new_activite = {
            "id_activite": 100,
            "nom": "Activité Test",
            "type_activite": "pilotee",
            "ids_exercices_inclus": [1, 2, 3]
        }
        status, data, error = self._request("POST", "/activites/", json=new_activite)
        if error:
            self.add_result("Create Activité", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 201:
            self.add_result("Create Activité", TestStatus.PASSED, "Activité créée")
            return True
        elif status == 404:
            self.add_result("Create Activité", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 4)")
            return True
        else:
            self.add_result("Create Activité", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_get_activite(self):
        """Teste GET /activites/{id}."""
        self.log("Test: Récupération d'une activité", "test")
        status, data, error = self._request("GET", "/activites/1")
        if error:
            self.add_result("Get Activité", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data:
            self.add_result("Get Activité", TestStatus.PASSED, "Activité récupérée")
            return True
        elif status == 404:
            self.add_result("Get Activité", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 4)")
            return True
        else:
            self.add_result("Get Activité", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_list_sessions(self):
        """Teste GET /sessions/."""
        self.log("Test: Liste des sessions", "test")
        status, data, error = self._request("GET", "/sessions/")
        if error:
            self.add_result("List Sessions", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and isinstance(data, list):
            self.add_result("List Sessions", TestStatus.PASSED, f"{len(data)} sessions")
            return True
        elif status == 404:
            self.add_result("List Sessions", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 4)")
            return True
        else:
            self.add_result("List Sessions", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_create_session(self):
        """Teste POST /sessions/ - démarrer une session."""
        self.log("Test: Création d'une session", "test")
        new_session = {
            "id_activite": 1,
            "id_apprenant": 1
        }
        status, data, error = self._request("POST", "/sessions/", json=new_session)
        if error:
            self.add_result("Create Session", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 201:
            self.add_result("Create Session", TestStatus.PASSED, "Session créée")
            return True
        elif status == 404:
            self.add_result("Create Session", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 4)")
            return True
        else:
            self.add_result("Create Session", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_get_bilan(self):
        """Teste GET /sessions/{id}/bilan - bilan de fin d'activité."""
        self.log("Test: Bilan de session", "test")
        status, data, error = self._request("GET", "/sessions/1/bilan")
        if error:
            self.add_result("Get Bilan", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data:
            self.add_result("Get Bilan", TestStatus.PASSED, "Bilan récupéré")
            return True
        elif status == 404:
            self.add_result("Get Bilan", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 4)")
            return True
        else:
            self.add_result("Get Bilan", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_close_session(self):
        """Teste PATCH /sessions/{id}/cloturer."""
        self.log("Test: Clôture d'une session", "test")
        status, data, error = self._request("PATCH", "/sessions/1/cloturer")
        if error:
            self.add_result("Close Session", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200:
            self.add_result("Close Session", TestStatus.PASSED, "Session clôturée")
            return True
        elif status == 404:
            self.add_result("Close Session", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 4)")
            return True
        else:
            self.add_result("Close Session", TestStatus.FAILED, f"Status: {status}")
            return False

    def run_all_tests(self):
        """Exécute tous les tests."""
        print("\n" + "=" * 70)
        print("  PLATONAAV - TESTS GROUPE 4 (Activités Pédagogiques)")
        print("=" * 70)
        print(f"\n🌐 URL: {self.base_url}")
        print(f"📦 Client: {'httpx' if HAS_HTTPX else 'urllib (fallback)'}")
        print()

        # Partie Commune
        print("-" * 70)
        print("🔌 PARTIE COMMUNE - Tests de base")
        print("-" * 70)
        self.test_root_endpoint()
        self.test_health_check()
        self.test_list_aavs()

        # Partie Spécifique
        print("\n" + "-" * 70)
        print("📚 PARTIE SPECIFIQUE - Groupe 4 (Activités Pédagogiques)")
        print("-" * 70)
        self.test_list_activites()
        self.test_create_activite()
        self.test_get_activite()
        self.test_list_sessions()
        self.test_create_session()
        self.test_get_bilan()
        self.test_close_session()

        # Résumé
        self.print_summary()

    def print_summary(self):
        """Affiche le résumé des tests."""
        print("\n" + "=" * 70)
        print("  RÉSULTATS")
        print("=" * 70)

        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)

        print(f"\n  ✅ Réussis:  {passed}")
        print(f"  ❌ Échoués: {failed}")
        print(f"  💥 Erreurs:  {errors}")
        print(f"  ⏭️  Ignorés: {skipped}")
        print(f"\n  📊 Total:    {len(self.results)} tests")

        if failed > 0 or errors > 0:
            print("\n" + "-" * 70)
            print("  DÉTAILS DES ÉCHECS")
            print("-" * 70)
            for result in self.results:
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"\n  {result.name}")
                    print(f"     Status: {result.status.value}")
                    print(f"     Message: {result.message}")

        print("\n" + "=" * 70)
        return failed == 0 and errors == 0


def main():
    parser = argparse.ArgumentParser(description="Tests pour le Groupe 4 - Activités Pédagogiques")
    parser.add_argument("--url", default="http://localhost:8000", help="URL de l'API")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    args = parser.parse_args()

    tester = BaseTester(base_url=args.url, verbose=args.verbose)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
