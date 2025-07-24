# Ticket Categorization Automation

An automated system for classifying support tickets using OpenAI's GPT models. This tool analyzes support ticket text and categorizes it according to a customizable taxonomy.

## Overview

This project provides a solution for automatically categorizing support tickets based on their content. It uses OpenAI's GPT models to analyze ticket text and classify it into appropriate categories and subcategories. The system supports:

1. **Single Category Classification**: Identifying the primary issue type and subcategory
2. **Multi-Issue Extraction**: Detecting multiple aspects that need classification within a single ticket
3. **Dynamic Category Loading**: Reading categories from a JSON file at runtime, supporting nested category structures

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/Ticket_Categorization_Automation.git
   cd Ticket_Categorization_Automation
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the provided `.env.example`:
   ```
   cp .env.example .env
   ```

4. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   MODEL=gpt-4.1
   TIMEOUT_SECONDS=30
   ```

## Configuration

The system uses the following configuration parameters:

- `OPENAI_API_KEY`: Your OpenAI API key
- `MODEL`: The OpenAI model to use (default: gpt-4.1)
- `TIMEOUT_SECONDS`: Timeout for API calls (default: 30)

These can be configured in the `.env` file.

## Usage

### Basic Usage

```python
from ticket_classifier.data_loader import load_data
from ticket_classifier.llm_client import LLMClient

# Load ticket and categories
ticket_text, categories = load_data(
    "data/tickets/sample_ticket.txt",
    "data/categories/categories.json"
)

# Initialize the LLM client
client = LLMClient()

# Classify the ticket
result = client.classify(ticket_text, categories)
print(result)
```

### Command Line Usage

#### Using main.py (Recommended)

The easiest way to use the ticket classifier is through the main.py script:

```bash
# Basic usage
python main.py --ticket data/tickets/sample_ticket.txt --categories data/categories/categories.json

# With short options
python main.py -t data/tickets/sample_ticket.txt -c data/categories/categories.json

# Save results to a file
python main.py -t data/tickets/sample_ticket.txt -c data/categories/categories.json -o results.json

# Enable verbose logging
python main.py -t data/tickets/sample_ticket.txt -c data/categories/categories.json -v
```

The main.py script provides:
- Formatted output for easy reading
- Command-line argument parsing
- Error handling
- Option to save results to a file
- Verbose logging mode

#### Using Module Directly

You can also run the ticket classifier modules directly:

```bash
# Run the LLM classifier on a ticket
python -m ticket_classifier.llm_client data/tickets/sample_ticket.txt data/categories/categories.json
```

This command will:
1. Load the ticket text from the specified file
2. Load the categories from the JSON file
3. Use the OpenAI API to classify the ticket
4. Display the classification results

You can also use the data loader to view ticket and category data without classification:

```bash
python -m ticket_classifier.data_loader data/tickets/sample_ticket.txt data/categories/categories.json
```

## Project Structure

```
Ticket_Categorization_Automation/
├── data/
│   ├── categories/
│   │   └── categories.json    # Category taxonomy definition
│   └── tickets/
│       └── sample_ticket.txt  # Example support ticket
├── tests/
│   └── test_data_loader.py    # Unit tests for data loading
├── ticket_classifier/
│   ├── __init__.py
│   ├── config.py              # Configuration and environment variables
│   ├── data_loader.py         # Functions for loading tickets and categories
│   └── llm_client.py          # OpenAI API integration for classification
├── .env.example               # Template for environment variables
├── .gitignore
├── main.py                    # Main entry point with CLI interface
└── README.md
```

## Classification Output

The system provides three types of classification:

1. **Case 1**: Single category classification with category and subcategory
2. **Case 2**: Multi-issue extraction with categories, subcategories, and reasons
3. **Case 3**: Dynamic category classification with categories, subcategories, and comments

Example output:

```json
{
  "case_1": {
    "category": "Issue Type",
    "subcategory": "Bug"
  },
  "case_2": [
    {
      "category": "Issue Type",
      "subcategories": ["Bug"],
      "reason": ["The dashboard is not loading as expected"]
    },
    {
      "category": "Priority",
      "subcategories": ["High", "User Experience"],
      "reason": ["Affecting user experience and business metrics"]
    }
  ],
  "case_3": [
    {
      "category": "Component",
      "subcategories": ["Frontend", "Mobile"],
      "comment": "The issue is specific to mobile devices"
    }
  ]
}
```

## Testing

Run the tests using pytest:

```
pytest tests/
```