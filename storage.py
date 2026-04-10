import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config import SAVED_PRDS_DIR

_dir = Path(SAVED_PRDS_DIR)


def _ensure_dir():
    _dir.mkdir(parents=True, exist_ok=True)


def save_prd(inputs: dict, markdown: str, prd_id: str | None = None) -> str:
    """Persist a PRD (inputs + generated markdown) as a JSON file. Returns the ID."""
    _ensure_dir()
    if prd_id is None:
        prd_id = uuid.uuid4().hex[:12]

    path = _dir / f"{prd_id}.json"
    now = datetime.now(timezone.utc).isoformat()

    data: dict
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        data["updated_at"] = now
    else:
        data = {"created_at": now, "updated_at": now}

    data["inputs"] = inputs
    data["markdown"] = markdown

    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    return prd_id


def load_prd(prd_id: str) -> dict | None:
    """Load a saved PRD by ID. Returns None if not found."""
    path = _dir / f"{prd_id}.json"
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    data["id"] = prd_id
    return data


def list_saved_prds() -> list[dict]:
    """Return a list of saved PRD summaries sorted by most recently updated."""
    _ensure_dir()
    results = []
    for p in _dir.glob("*.json"):
        try:
            with open(p) as f:
                data = json.load(f)
            inputs = data.get("inputs", {})
            results.append({
                "id": p.stem,
                "name": inputs.get("product_name", "Untitled"),
                "domain": inputs.get("domain", ""),
                "updated_at": data.get("updated_at", ""),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    results.sort(key=lambda r: r["updated_at"], reverse=True)
    return results


def delete_prd(prd_id: str) -> bool:
    """Delete a saved PRD. Returns True if deleted, False if not found."""
    path = _dir / f"{prd_id}.json"
    if path.exists():
        os.remove(path)
        return True
    return False
