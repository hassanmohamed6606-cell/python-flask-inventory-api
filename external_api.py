import requests

BASE_URL = "https://world.openfoodfacts.org"


def lookup_product(barcode=None, name=None):
    """Return OpenFoodFacts product details and an HTTP-style status code."""
    try:
        if barcode:
            response = requests.get(
                f"{BASE_URL}/api/v2/product/{barcode}.json",
                timeout=10,
                headers={"User-Agent": "InventoryManagementStudentProject/1.0"},
            )
        elif name:
            response = requests.get(
                f"{BASE_URL}/cgi/search.pl",
                params={"search_terms": name, "search_simple": 1, "action": "process",
                        "json": 1, "page_size": 1},
                timeout=10,
                headers={"User-Agent": "InventoryManagementStudentProject/1.0"},
            )
        else:
            return {"error": "Provide a barcode or product name"}, 400

        response.raise_for_status()
        payload = response.json()
        if barcode:
            if payload.get("status") != 1 or not payload.get("product"):
                return {"error": "Product not found", "source": "OpenFoodFacts"}, 404
            return payload, 200

        products = payload.get("products", [])
        if not products:
            return {"error": "Product not found", "source": "OpenFoodFacts"}, 404
        return {"status": 1, "product": products[0]}, 200
    except requests.RequestException as exc:
        return {"error": "External product service is unavailable", "details": str(exc)}, 502
    except ValueError:
        return {"error": "External service returned invalid JSON"}, 502
