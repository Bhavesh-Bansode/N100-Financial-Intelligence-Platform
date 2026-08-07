"""Export the current FastAPI OpenAPI schema and a matching Postman collection.

Run with ``python -m src.api.export_specs`` from the project root.
"""

import json
from pathlib import Path

from src.api.main import API_VERSION, app


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = PROJECT_ROOT /"docs"


def main() -> None:
    """Write OpenAPI and Postman JSON exports to the documentation folder."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    openapi = app.openapi()
    (DOCS_DIR / "openapi.json").write_text(json.dumps(openapi, indent=2), encoding="utf-8")

    items = []
    for path, operations in openapi["paths"].items():
        for method, operation in operations.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            postman_path = path
            for parameter in operation.get("parameters", []):
                if parameter.get("in") == "path":
                    name = parameter["name"]
                    postman_path = postman_path.replace("{" + name + "}", "{{" + name + "}}")
            items.append({
                "name": operation.get("summary", f"{method.upper()} {path}"),
                "request": {"method": method.upper(), "url": "{{baseUrl}}" + postman_path},
            })
    collection = {
        "info": {
            "name": "Nifty 100 Financial Intelligence API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "version": API_VERSION,
        },
        "variable": [{"key": "baseUrl", "value": "http://127.0.0.1:8000"}],
        "item": items,
    }
    (DOCS_DIR / "postman_collection.json").write_text(
        json.dumps(collection, indent=2), encoding="utf-8"
    )
    print(f"Exported {len(items)} requests to {DOCS_DIR}")


if __name__ == "__main__":
    main()
