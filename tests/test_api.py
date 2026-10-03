import pytest
import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.inventory.clear()
    app_module.inventory.extend([
        {"id": 1, "name": "Test item", "brand": "Brand", "barcode": "123",
         "price": 2.5, "stock": 4, "ingredients": ""}
    ])
    app_module.next_id = 2
    return app_module.app.test_client()


def test_get_all_and_one(client):
    assert client.get("/inventory").status_code == 200
    assert client.get("/inventory/1").json["name"] == "Test item"
    assert client.get("/inventory/99").status_code == 404


def test_create_item(client):
    response = client.post("/inventory", json={"name": "Tea", "price": 4, "stock": 8})
    assert response.status_code == 201
    assert response.json["id"] == 2
    assert client.get("/inventory/2").status_code == 200


def test_create_validation(client):
    assert client.post("/inventory", json={"name": "Tea"}).status_code == 400
    assert client.post("/inventory", json={"name": "Tea", "price": -1, "stock": 2}).status_code == 400


def test_patch_item(client):
    response = client.patch("/inventory/1", json={"stock": 10, "price": 3})
    assert response.status_code == 200
    assert response.json["stock"] == 10
    assert client.patch("/inventory/99", json={"stock": 1}).status_code == 404


def test_delete_item(client):
    assert client.delete("/inventory/1").status_code == 200
    assert client.get("/inventory/1").status_code == 404
    assert client.delete("/inventory/99").status_code == 404


def test_external_lookup_routes(client, monkeypatch):
    def fake_lookup(barcode=None, name=None):
        return {"status": 1, "product": {"product_name": "Mock Milk", "brands": "Mock"}}, 200
    monkeypatch.setattr(app_module, "lookup_product", fake_lookup)
    assert client.get("/lookup?name=milk").json["product"]["product_name"] == "Mock Milk"
    assert client.get("/lookup/barcode/123").status_code == 200
    imported = client.post("/inventory/from-api", json={"name": "milk"})
    assert imported.status_code == 201
    assert imported.json["name"] == "Mock Milk"
