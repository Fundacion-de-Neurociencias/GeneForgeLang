import json
import os

STORE_PATH = os.path.join(os.path.dirname(__file__), "axiom_store.json")

def load_axiom_store():
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH, "r") as f:
        return json.load(f)

def save_axiom_store(store):
    with open(STORE_PATH, "w") as f:
        json.dump(store, f, indent=4)

def get_axioms(confidence_min=0.8):
    store = load_axiom_store()
    return {k: v for k, v in store.items() if v.get("confidence", 0) >= confidence_min}
