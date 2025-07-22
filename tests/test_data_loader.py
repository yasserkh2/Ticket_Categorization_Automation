import sys
import pathlib

# 1. Add project-root to sys.path so Python can find ticket_classifier
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest
import json

from ticket_classifier.data_loader import (
    load_ticket,
    load_categories,
    load_data,
    TicketLoadError,
    CategoriesLoadError,
)

def test_load_ticket_success(tmp_path):
    ticket_file = tmp_path / "ticket.txt"
    content = "Sample support ticket text."
    ticket_file.write_text(content, encoding="utf-8")
    assert load_ticket(str(ticket_file)) == content

def test_load_ticket_not_found(tmp_path):
    missing = tmp_path / "no_ticket.txt"
    with pytest.raises(TicketLoadError):
        load_ticket(str(missing))

def test_load_categories_success(tmp_path):
    categories_file = tmp_path / "categories.json"
    data = [{"value": "Issue Type", "subcategories": [{"value": "Bug"}]}]
    categories_file.write_text(json.dumps(data), encoding="utf-8")
    assert load_categories(str(categories_file)) == data

def test_load_categories_not_found(tmp_path):
    missing = tmp_path / "no_categories.json"
    with pytest.raises(CategoriesLoadError):
        load_categories(str(missing))

def test_load_categories_invalid_json(tmp_path):
    categories_file = tmp_path / "bad.json"
    categories_file.write_text("{ invalid json }", encoding="utf-8")
    with pytest.raises(CategoriesLoadError):
        load_categories(str(categories_file))

def test_load_data_success(tmp_path):
    ticket_file = tmp_path / "ticket.txt"
    ticket_content = "Another support ticket."
    ticket_file.write_text(ticket_content, encoding="utf-8")

    categories_file = tmp_path / "categories.json"
    categories_content = [{"value": "Priority", "subcategories": []}]
    categories_file.write_text(json.dumps(categories_content), encoding="utf-8")

    ticket, categories = load_data(str(ticket_file), str(categories_file))
    assert ticket == ticket_content
    assert categories == categories_content

def test_load_data_ticket_error(tmp_path):
    categories_file = tmp_path / "categories.json"
    categories_file.write_text(json.dumps([{"value":"X","subcategories":[]}]), encoding="utf-8")
    with pytest.raises(TicketLoadError):
        load_data(str(tmp_path / "no_ticket.txt"), str(categories_file))

def test_load_data_categories_error(tmp_path):
    ticket_file = tmp_path / "ticket.txt"
    ticket_file.write_text("Hi", encoding="utf-8")
    with pytest.raises(CategoriesLoadError):
        load_data(str(ticket_file), str(tmp_path / "no_categories.json"))
