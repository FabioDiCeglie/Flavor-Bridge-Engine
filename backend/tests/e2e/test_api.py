"""
API Integration Tests for Flavor Bridge Engine.

Run with: python tests/test_api.py
Requires: httpx (pip install httpx)
"""
import asyncio
import httpx
import os
import sys

BASE_URL = os.environ.get("API_URL", "http://localhost:8787")


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"


def log_pass(name: str):
    print(f"{Colors.GREEN}✓ PASS{Colors.RESET} {name}")


def log_fail(name: str, error: str):
    print(f"{Colors.RED}✗ FAIL{Colors.RESET} {name}: {error}")


async def test_health(client: httpx.AsyncClient) -> bool:
    """Test GET /health returns 204."""
    try:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"
        log_pass("GET /health returns 204")
        return True
    except Exception as e:
        log_fail("GET /health returns 204", str(e))
        return False


async def test_search(client: httpx.AsyncClient) -> bool:
    """Test GET /search?q=Miso returns matches."""
    try:
        response = await client.get(f"{BASE_URL}/search", params={"q": "Miso"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["query"] == "Miso"
        assert isinstance(data["matches"], list)
        assert len(data["matches"]) > 0, "Expected at least one match"
        log_pass("GET /search?q=Miso returns matches")
        # Show top 3 matches
        for m in data["matches"][:3]:
            print(f"       → {m['name']} (score: {m['score']:.2f})")
        return True
    except Exception as e:
        log_fail("GET /search?q=Miso returns matches", str(e))
        return False


async def test_explain(client: httpx.AsyncClient) -> bool:
    """Test POST /explain returns AI explanation."""
    try:
        payload = {
            "query": "Miso",
            "matches": [
                {"name": "Soy Sauce", "description": "Fermented soybean condiment."},
                {"name": "Parmesan", "description": "Aged cheese rich in glutamates."},
            ]
        }
        response = await client.post(f"{BASE_URL}/explain", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "explanation" in data
        assert len(data["explanation"]) > 50, "Expected meaningful explanation"
        log_pass("POST /explain returns AI explanation")
        # Show truncated explanation
        explanation = data["explanation"][:150] + "..." if len(data["explanation"]) > 150 else data["explanation"]
        print(f"       → \"{explanation}\"")
        return True
    except Exception as e:
        log_fail("POST /explain returns AI explanation", str(e))
        return False


async def run_tests():
    """Run all tests."""
    print("\n🧪 Flavor Bridge Engine - API Tests")
    print(f"   Target: {BASE_URL}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check if server is running
        try:
            await client.get(f"{BASE_URL}/health")
        except httpx.ConnectError:
            print(f"{Colors.RED}ERROR:{Colors.RESET} Server not running at {BASE_URL}")
            print("Start the server first: npx wrangler dev")
            sys.exit(1)

        results = [
            await test_health(client),
            await test_search(client),
            await test_explain(client),
        ]

        # Summary
        passed = sum(results)
        total = len(results)
        print()
        if passed == total:
            print(f"{Colors.GREEN}All tests passed! ({passed}/{total}){Colors.RESET}\n")
        else:
            print(f"{Colors.RED}Tests failed: {passed}/{total} passed{Colors.RESET}\n")

        sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(run_tests())
