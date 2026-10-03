import argparse
import json
import requests

DEFAULT_API = "http://127.0.0.1:5000"


def call_api(method, path, base_url=DEFAULT_API, payload=None):
    """Make an API request; separated out to make CLI behavior easy to test."""
    try:
        response = requests.request(method, base_url + path, json=payload, timeout=10)
        try:
            body = response.json()
        except ValueError:
            body = {"error": response.text}
        return response.status_code, body
    except requests.RequestException as exc:
        return 0, {"error": f"Could not connect to API: {exc}"}


def print_result(status, body):
    print(f"HTTP {status}")
    print(json.dumps(body, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Inventory Management CLI")
    parser.add_argument("--url", default=DEFAULT_API, help="Base URL of the Flask API")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all inventory items")
    get = sub.add_parser("get", help="View one item"); get.add_argument("id", type=int)
    add = sub.add_parser("add", help="Add an inventory item")
    add.add_argument("--name", required=True); add.add_argument("--price", required=True, type=float)
    add.add_argument("--stock", required=True, type=int); add.add_argument("--brand", default="")
    add.add_argument("--barcode", default="")
    update = sub.add_parser("update", help="Update price, stock, or other fields")
    update.add_argument("id", type=int); update.add_argument("--price", type=float)
    update.add_argument("--stock", type=int); update.add_argument("--name")
    delete = sub.add_parser("delete", help="Delete an item"); delete.add_argument("id", type=int)
    lookup = sub.add_parser("find", help="Search OpenFoodFacts"); lookup.add_argument("--name")
    lookup.add_argument("--barcode")
    import_api = sub.add_parser("import", help="Look up and add a product from OpenFoodFacts")
    import_api.add_argument("--name"); import_api.add_argument("--barcode")

    args = parser.parse_args()
    if args.command == "list":
        method, path, payload = "GET", "/inventory", None
    elif args.command == "get":
        method, path, payload = "GET", f"/inventory/{args.id}", None
    elif args.command == "add":
        method, path, payload = "POST", "/inventory", {
            "name": args.name, "price": args.price, "stock": args.stock,
            "brand": args.brand, "barcode": args.barcode}
    elif args.command == "update":
        payload = {k: v for k, v in {"price": args.price, "stock": args.stock,
                                     "name": args.name}.items() if v is not None}
        if not payload:
            parser.error("update requires at least one of --price, --stock, or --name")
        method, path = "PATCH", f"/inventory/{args.id}"
    elif args.command == "delete":
        method, path, payload = "DELETE", f"/inventory/{args.id}", None
    elif args.command == "find":
        if not args.name and not args.barcode:
            parser.error("find requires --name or --barcode")
        method = "GET"
        path = f"/lookup/barcode/{args.barcode}" if args.barcode else "/lookup?name=" + requests.utils.quote(args.name)
        payload = None
    else:
        if not args.name and not args.barcode:
            parser.error("import requires --name or --barcode")
        method, path = "POST", "/inventory/from-api"
        payload = {"name": args.name, "barcode": args.barcode}

    status, body = call_api(method, path, args.url, payload)
    print_result(status, body)


if __name__ == "__main__":
    main()
