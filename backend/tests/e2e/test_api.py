"""
API Integration Tests for Flavor Bridge Engine.

Run with: python tests/test_api.py
Requires: httpx (pip install httpx)
"""
import asyncio
import httpx
import os
import sys
import time

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
    """Test GET /search?q=Miso returns matches with id, score, name, description, compounds."""
    try:
        response = await client.get(f"{BASE_URL}/search", params={"q": "Miso"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["query"] == "Miso"
        assert isinstance(data["matches"], list)
        assert len(data["matches"]) > 0, "Expected at least one match"
        for m in data["matches"]:
            assert "id" in m and "score" in m and "name" in m and "description" in m and "compounds" in m
        # Query ingredient is excluded from matches
        names = [m["name"].lower() for m in data["matches"]]
        assert "miso" not in names, "Query ingredient should not appear in matches"
        log_pass("GET /search?q=Miso returns matches (with compounds)")
        for m in data["matches"][:3]:
            print(f"       → {m['name']} (score: {m['score']:.2f})")
        return True
    except Exception as e:
        log_fail("GET /search?q=Miso returns matches", str(e))
        return False


async def test_search_unknown_ingredient(client: httpx.AsyncClient) -> bool:
    """Test GET /search?q=NotAnIngredient returns 404."""
    try:
        response = await client.get(f"{BASE_URL}/search", params={"q": "NotAnIngredientXYZ"})
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert data.get("error") == "Ingredient not found"
        assert data.get("query") == "NotAnIngredientXYZ"
        assert "message" in data
        log_pass("GET /search unknown ingredient returns 404")
        return True
    except Exception as e:
        log_fail("GET /search unknown ingredient returns 404", str(e))
        return False


async def test_explain(client: httpx.AsyncClient) -> bool:
    """Test POST /explain returns AI explanation."""
    try:
        payload = {
            "query": "Ginseng",
            "matches": [
                {"id": "625", "score": 0.81833684, "name": "Pepper (C. chinense)", "description": "Capsicum chinense, is a species of chili pepper native to the Americas. C. chinense varieties are well known for their exceptional heat and unique flavors. C. chinense is native to Central America, the Yucatan region, and the Caribbean islands. Despite its name, C. chinense or \"Chinese capsicum\" is misleading. All Capsicum species originated in the New World. Nikolaus Joseph von Jacquin (1727\u20131817), a Dutch botanist, erroneously named the species in 1776, because he believed they originated in", "compounds": "(+)-7-iso-jasmonate, (+)-cis-abscisic aldehyde, (+)-lariciresinol, (+)-marmesin, (+)-Neomenthol, (+)-Pinoresinol, (+)-pulegone, (+)-Secoisolariciresinol, (+)-taxifolin, (-)-jasmonoyl-L-isoleucine, (-)-lactol, (-)-Lariciresinol, (-)-Maackiain, (-)-maackiain-3-O-glucoside, (-)-Matairesinol, (-)-medicarpin, (-)-medicarpin-3-O-glucoside, (-)-Menthone, (-)-phaseollidin, (-)-Pinoresinol"},
                {"id": "627", "score": 0.8169661, "name": "Pepper (C. pubescens)", "description": "Capsicum pubescens is a species of the genus Capsicum (pepper), which is found primarily in Central and South America. The plants, but especially the fruits, are often referred to as \"rocoto\":http://en.wikipedia.org/wiki/Rocoto and locoto. As they reach a relatively advanced age and the roots lignify quickly, sometimes the familiar name is tree chili. Of all the domesticated species of peppers, this is the least widespread and systematically furthest away from all others. [Wikipedia] See a \"l", "compounds": "(+)-7-iso-jasmonate, (+)-cis-abscisic aldehyde, (+)-lariciresinol, (+)-marmesin, (+)-Neomenthol, (+)-Pinoresinol, (+)-pulegone, (+)-Secoisolariciresinol, (+)-taxifolin, (-)-jasmonoyl-L-isoleucine, (-)-lactol, (-)-Lariciresinol, (-)-Maackiain, (-)-maackiain-3-O-glucoside, (-)-Matairesinol, (-)-medicarpin, (-)-medicarpin-3-O-glucoside, (-)-Menthone, (-)-phaseollidin, (-)-Pinoresinol"},

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


async def test_search_cache(client: httpx.AsyncClient) -> bool:
    """Test search caching returns X-Cache: HIT on second request."""
    try:
        # First request - should be MISS
        start1 = time.time()
        response1 = await client.get(f"{BASE_URL}/search", params={"q": "Cherry tomato"})
        time1 = time.time() - start1
        assert response1.status_code == 200, f"Expected 200, got {response1.status_code}"
        cache1 = response1.headers.get("x-cache", "").upper()
        
        # Second request - should be HIT
        start2 = time.time()
        response2 = await client.get(f"{BASE_URL}/search", params={"q": "Cherry tomato"})
        time2 = time.time() - start2
        assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
        cache2 = response2.headers.get("x-cache", "").upper()
        
        assert cache2 == "HIT", f"Expected X-Cache: HIT, got {cache2}"
        
        saved = time1 - time2
        log_pass("Search caching returns X-Cache: HIT")
        print(f"       → 1st: {cache1} ({time1:.2f}s), 2nd: {cache2} ({time2:.2f}s), saved: {saved:.2f}s")
        return True
    except Exception as e:
        log_fail("Search caching returns X-Cache: HIT", str(e))
        return False


async def test_explain_cache(client: httpx.AsyncClient) -> bool:
    """Test explain caching returns X-Cache: HIT on second request."""
    try:
        payload = {
            "query": "Ginseng",
            "matches": [
                {"id": "625", "score": 0.81833684, "name": "Pepper (C. chinense)", "description": "Capsicum chinense, is a species of chili pepper native to the Americas. C. chinense varieties are well known for their exceptional heat and unique flavors. C. chinense is native to Central America, the Yucatan region, and the Caribbean islands. Despite its name, C. chinense or \"Chinese capsicum\" is misleading. All Capsicum species originated in the New World. Nikolaus Joseph von Jacquin (1727\u20131817), a Dutch botanist, erroneously named the species in 1776, because he believed they originated in", "compounds": "(+)-7-iso-jasmonate, (+)-cis-abscisic aldehyde, (+)-lariciresinol, (+)-marmesin, (+)-Neomenthol, (+)-Pinoresinol, (+)-pulegone, (+)-Secoisolariciresinol, (+)-taxifolin, (-)-jasmonoyl-L-isoleucine, (-)-lactol, (-)-Lariciresinol, (-)-Maackiain, (-)-maackiain-3-O-glucoside, (-)-Matairesinol, (-)-medicarpin, (-)-medicarpin-3-O-glucoside, (-)-Menthone, (-)-phaseollidin, (-)-Pinoresinol"},
                {"id": "627", "score": 0.8169661, "name": "Pepper (C. pubescens)", "description": "Capsicum pubescens is a species of the genus Capsicum (pepper), which is found primarily in Central and South America. The plants, but especially the fruits, are often referred to as \"rocoto\":http://en.wikipedia.org/wiki/Rocoto and locoto. As they reach a relatively advanced age and the roots lignify quickly, sometimes the familiar name is tree chili. Of all the domesticated species of peppers, this is the least widespread and systematically furthest away from all others. [Wikipedia] See a \"l", "compounds": "(+)-7-iso-jasmonate, (+)-cis-abscisic aldehyde, (+)-lariciresinol, (+)-marmesin, (+)-Neomenthol, (+)-Pinoresinol, (+)-pulegone, (+)-Secoisolariciresinol, (+)-taxifolin, (-)-jasmonoyl-L-isoleucine, (-)-lactol, (-)-Lariciresinol, (-)-Maackiain, (-)-maackiain-3-O-glucoside, (-)-Matairesinol, (-)-medicarpin, (-)-medicarpin-3-O-glucoside, (-)-Menthone, (-)-phaseollidin, (-)-Pinoresinol"},

            ]
        }
        
        # First request - should be MISS
        start1 = time.time()
        response1 = await client.post(f"{BASE_URL}/explain", json=payload)
        time1 = time.time() - start1
        assert response1.status_code == 200, f"Expected 200, got {response1.status_code}"
        cache1 = response1.headers.get("x-cache", "").upper()
        
        # Second request - should be HIT
        start2 = time.time()
        response2 = await client.post(f"{BASE_URL}/explain", json=payload)
        time2 = time.time() - start2
        assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
        cache2 = response2.headers.get("x-cache", "").upper()
        
        assert cache2 == "HIT", f"Expected X-Cache: HIT, got {cache2}"
        
        saved = time1 - time2
        log_pass("Explain caching returns X-Cache: HIT")
        print(f"       → 1st: {cache1} ({time1:.2f}s), 2nd: {cache2} ({time2:.2f}s), saved: {saved:.2f}s")
        return True
    except Exception as e:
        log_fail("Explain caching returns X-Cache: HIT", str(e))
        return False


async def test_rate_limit(client: httpx.AsyncClient) -> bool:
    """Test rate limiting returns 429 after too many requests)."""
    try:
        # Make 15 requests - should hit the limit (10/min)
        responses = []
        for _ in range(15):
            response = await client.get(f"{BASE_URL}/search", params={"q": "Parmesan cheese"})
            responses.append(response.status_code)
        
        # Should have some 200s and some 429s
        count_200 = responses.count(200)
        count_429 = responses.count(429)
        
        assert count_429 > 0, "Expected at least one 429 response"
        assert count_200 > 0, "Expected at least one 200 response"
        
        log_pass("Rate limiting returns 429 after limit exceeded")
        print(f"       → {count_200} allowed, {count_429} blocked (previous tests used some quota)")
        return True
    except Exception as e:
        log_fail("Rate limiting returns 429 after limit exceeded", str(e))
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
            await test_search_unknown_ingredient(client),
            await test_search_cache(client),
            await test_explain(client),
            await test_explain_cache(client),
            await test_rate_limit(client),
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
