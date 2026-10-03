# Inventory Management System

A beginner-friendly Flask REST API, command-line client, and pytest suite. Inventory is stored in a Python list, so it resets when the server restarts. OpenFoodFacts supplies optional product details.

## Project files

- `app.py` — Flask routes and in-memory inventory
- `external_api.py` — OpenFoodFacts integration
- `cli.py` — command-line client
- `tests/` — API and CLI tests
- `requirements.txt` — dependencies

Started the API in one terminal:

```powershell
py app.py
```

The API runs at `http://127.0.0.1:5000`. Keep this terminal open. Use a second terminal in the same folder for CLI commands.

## CLI examples

```powershell
py cli.py list
py cli.py get 1
py cli.py add --name "Green Tea" --price 5.25 --stock 12 --brand "Example"
py cli.py update 1 --price 4.10 --stock 25
py cli.py delete 2
py cli.py find --name "almond milk"
py cli.py find --barcode 3017620422003
py cli.py import --barcode 3017620422003
```

Use `py cli.py --help` or `py cli.py add --help` to see options. To use a different API URL, add `--url http://host:port` before the command.

## REST endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/inventory` | List all items |
| GET | `/inventory/<id>` | Retrieve one item |
| POST | `/inventory` | Create an item |
| PATCH | `/inventory/<id>` | Partially update an item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/lookup?name=<name>` | Search OpenFoodFacts by name |
| GET | `/lookup/barcode/<barcode>` | Fetch OpenFoodFacts item by barcode |
| POST | `/inventory/from-api` | Look up and add a product to inventory |

Example JSON for `POST /inventory`:

```json
{
  "name": "Organic Almond Milk",
  "brand": "Silk",
  "barcode": "0123456789012",
  "price": 3.99,
  "stock": 20,
  "ingredients": "Filtered water, almonds, cane sugar"
}
```

The API validates required fields and non-negative price/stock values. Product imports set price and stock to `0` because OpenFoodFacts is a food-product database, not a store's pricing or stock system. Employees can update those fields afterward.

## Runned tests

With the virtual environment active:

```powershell
py -m pytest -v
```

External API calls are mocked in tests, so the test suite does not depend on internet access.
