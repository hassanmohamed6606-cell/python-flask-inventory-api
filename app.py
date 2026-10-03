from flask import Flask, jsonify, request
from external_api import lookup_product

app = Flask(__name__)

inventory = [
    {"id": 1, "name": "Organic Almond Milk", "brand": "Silk", "barcode": "0123456789012",
     "price": 3.99, "stock": 20, "ingredients": "Filtered water, almonds, cane sugar"},
    {"id": 2, "name": "Rolled Oats", "brand": "Example Foods", "barcode": "0987654321098",
     "price": 2.49, "stock": 35, "ingredients": "Whole grain oats"},
]
next_id = 3


@app.get("/")
def home():
    return jsonify({"message": "Inventory Management API", "endpoints": [
        "GET /inventory", "GET /inventory/<id>", "POST /inventory",
        "PATCH /inventory/<id>", "DELETE /inventory/<id>",
        "GET /lookup?name=<product name>", "GET /lookup/barcode/<barcode>"
    ]})


@app.get("/inventory")
def get_inventory():
    return jsonify(inventory), 200


@app.get("/inventory/<int:item_id>")
def get_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404
    return jsonify(item), 200


@app.post("/inventory")
def add_item():
    global next_id
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    required = ("name", "price", "stock")
    missing = [key for key in required if key not in data]
    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400
    try:
        price = float(data["price"])
        stock = int(data["stock"])
        if price < 0 or stock < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "price must be non-negative and stock a non-negative integer"}), 400

    item = {
        "id": next_id,
        "name": str(data["name"]).strip(),
        "brand": data.get("brand", ""),
        "barcode": data.get("barcode", ""),
        "price": price,
        "stock": stock,
        "ingredients": data.get("ingredients", ""),
    }
    if not item["name"]:
        return jsonify({"error": "name cannot be empty"}), 400
    inventory.append(item)
    next_id += 1
    return jsonify(item), 201


@app.patch("/inventory/<int:item_id>")
def update_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Provide a non-empty JSON object"}), 400
    allowed = {"name", "brand", "barcode", "price", "stock", "ingredients"}
    unknown = set(data) - allowed
    if unknown:
        return jsonify({"error": "Unknown fields", "fields": sorted(unknown)}), 400
    updated = item.copy()
    updated.update(data)
    try:
        if "price" in data:
            updated["price"] = float(data["price"])
        if "stock" in data:
            updated["stock"] = int(data["stock"])
        if updated["price"] < 0 or updated["stock"] < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "price and stock must be non-negative numbers"}), 400
    if "name" in data and not str(updated["name"]).strip():
        return jsonify({"error": "name cannot be empty"}), 400
    inventory[inventory.index(item)] = updated
    return jsonify(updated), 200


@app.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    item = next((item for item in inventory if item["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404
    inventory.remove(item)
    return jsonify({"message": "Inventory item deleted", "id": item_id}), 200


@app.get("/lookup")
def lookup_by_name():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "Supply a product name using ?name=..."}), 400
    result, status = lookup_product(name=name)
    return jsonify(result), status


@app.get("/lookup/barcode/<barcode>")
def lookup_by_barcode(barcode):
    result, status = lookup_product(barcode=barcode)
    return jsonify(result), status


@app.post("/inventory/from-api")
def add_from_api():
    """Look up a product, then add the returned details to the in-memory inventory."""
    global next_id
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not (data.get("barcode") or data.get("name")):
        return jsonify({"error": "Provide barcode or name"}), 400
    result, status = lookup_product(barcode=data.get("barcode"), name=data.get("name"))
    if status != 200:
        return jsonify(result), status
    product = result.get("product", {})
    name = product.get("product_name") or data.get("name") or "Unknown product"
    item = {
        "id": next_id, "name": name, "brand": product.get("brands", ""),
        "barcode": data.get("barcode", product.get("code", "")),
        "price": 0.0, "stock": 0,
        "ingredients": product.get("ingredients_text", ""),
    }
    inventory.append(item)
    next_id += 1
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)
