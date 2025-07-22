# src/ticket_classifier/data_loader.py

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Exceptions your tests import
class TicketLoadError(Exception):
    """Raised when the ticket file cannot be loaded."""
    pass

class CategoriesLoadError(Exception):
    """Raised when the categories JSON cannot be loaded or parsed."""
    pass

logger = logging.getLogger(__name__)

def load_ticket(path: str) -> str:
    """
    Read and return the full text of a support ticket.

    Raises:
      TicketLoadError if the file is missing or unreadable.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError as e:
        logger.error(f"Ticket file not found: {path}")
        raise TicketLoadError(f"Ticket file not found: {path}") from e
    except OSError as e:
        logger.error(f"Error reading ticket file {path}: {e}")
        raise TicketLoadError(f"Error reading ticket file: {path}") from e

def load_categories(path: str) -> List[Dict[str, Any]]:
    """
    Read and return the parsed JSON taxonomy as a list of dicts.

    Raises:
      CategoriesLoadError if the file is missing or contains invalid JSON.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        logger.error(f"Categories file not found: {path}")
        raise CategoriesLoadError(f"Categories file not found: {path}") from e
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error loading categories from {path}: {e}")
        raise CategoriesLoadError(f"Error loading categories: {path}") from e

def load_data(
    ticket_path: str,
    categories_path: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Load both the ticket text and the parsed categories JSON.

    Returns:
      - ticket_text: str
      - raw_categories: List[Dict[str, Any]]

    Propagates:
      TicketLoadError, CategoriesLoadError
    """
    ticket_text = load_ticket(ticket_path)
    raw_categories = load_categories(categories_path)
    return ticket_text, raw_categories

if __name__ == "__main__":
    import sys

    # You can pass the file paths as command-line arguments, or hardcode them for quick testing:
    if len(sys.argv) != 3:
        print("Usage: python -m ticket_classifier.data_loader <ticket_path> <categories_path>")
        sys.exit(1)

    ticket_path = sys.argv[1]
    categories_path = sys.argv[2]

    try:
        ticket_text, categories = load_data(ticket_path, categories_path)
        print("\n=== Ticket Text ===")
        print(ticket_text)
        print("\n=== Categories JSON ===")
        import pprint
        pprint.pprint(categories)
    except TicketLoadError as e:
        print(f"Error loading ticket: {e}")
    except CategoriesLoadError as e:
        print(f"Error loading categories: {e}")
