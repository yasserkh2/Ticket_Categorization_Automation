import json
from typing import Any, Dict, List

def print_categories(categories: List[Dict[str, Any]]):
    for cat in categories:
        print(f"Category: {cat.get('value')}")
        print(f"  Description: {cat.get('description', 'No description')}")
        subcats = cat.get("subcategories", [])
        if subcats:
            print("  Subcategories:")
            for sub in subcats:
                print(f"    - {sub.get('value')}: {sub.get('description', 'No description')}")
        print("-" * 40)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python simple_category_parser.py <categories_json_path>")
        sys.exit(1)

    categories_path = sys.argv[1]
    with open(categories_path, "r", encoding="utf-8") as f:
        categories = json.load(f)

    print_categories(categories)
