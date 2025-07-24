#!/usr/bin/env python3
"""
Ticket Categorization Automation - Main Entry Point

This script provides a command-line interface for the ticket categorization system.
It loads a support ticket and a categories taxonomy, then uses OpenAI's GPT models
to classify the ticket into appropriate categories.

Usage:
    python main.py --ticket <ticket_file> --categories <categories_file>
    python main.py -t <ticket_file> -c <categories_file>
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

from ticket_classifier.data_loader import load_data, TicketLoadError, CategoriesLoadError
from ticket_classifier.llm_client import LLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Classify support tickets using OpenAI GPT models.'
    )
    parser.add_argument(
        '-t', '--ticket',
        required=True,
        help='Path to the ticket text file'
    )
    parser.add_argument(
        '-c', '--categories',
        required=True,
        help='Path to the categories JSON file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path to save the classification results (JSON format)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    return parser.parse_args()

def format_classification_result(result: Dict[str, Any]) -> str:
    """Format the classification result for display."""
    output = []
    
    # Case 1: Single category classification
    output.append("=== Single Category Classification ===")
    case_1 = result.get("case_1", {})
    if case_1:
        output.append(f"Category: {case_1.get('category', 'N/A')}")
        output.append(f"Subcategory: {case_1.get('subcategory', 'N/A')}")
    else:
        output.append("No single category classification available.")
    
    # Case 2: Multi-issue extraction
    output.append("\n=== Multi-Issue Extraction ===")
    case_2 = result.get("case_2", [])
    if case_2:
        for i, issue in enumerate(case_2, 1):
            output.append(f"\nIssue {i}:")
            output.append(f"  Category: {issue.get('category', 'N/A')}")
            subcats = issue.get('subcategories', [])
            output.append(f"  Subcategories: {', '.join(subcats) if subcats else 'N/A'}")
            reasons = issue.get('reason', [])
            if reasons:
                output.append("  Reasons:")
                for reason in reasons:
                    output.append(f"    - {reason}")
    else:
        output.append("No multi-issue extraction available.")
    
    # Case 3: Dynamic category classification
    output.append("\n=== Dynamic Category Classification ===")
    case_3 = result.get("case_3", [])
    if case_3:
        for i, category in enumerate(case_3, 1):
            output.append(f"\nClassification {i}:")
            output.append(f"  Category: {category.get('category', 'N/A')}")
            subcats = category.get('subcategories', [])
            output.append(f"  Subcategories: {', '.join(subcats) if subcats else 'N/A'}")
            comment = category.get('comment', '')
            if comment:
                output.append(f"  Comment: {comment}")
    else:
        output.append("No dynamic category classification available.")
    
    return "\n".join(output)

def save_results(result: Dict[str, Any], output_path: str) -> None:
    """Save the classification results to a JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save results to {output_path}: {e}")
        raise

def main():
    """Main entry point for the ticket classification system."""
    args = parse_arguments()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Loading ticket from {args.ticket}")
    logger.info(f"Loading categories from {args.categories}")
    
    try:
        # Load ticket and categories
        ticket_text, categories = load_data(args.ticket, args.categories)
        logger.debug(f"Loaded ticket ({len(ticket_text)} chars)")
        logger.debug(f"Loaded {len(categories)} top-level categories")
        
        # Initialize LLM client and classify ticket
        logger.info("Initializing LLM client")
        client = LLMClient()
        
        logger.info("Classifying ticket...")
        result = client.classify(ticket_text, categories)
        
        # Display results
        print("\n" + format_classification_result(result))
        
        # Save results if output path is provided
        if args.output:
            save_results(result, args.output)
            print(f"\nResults saved to {args.output}")
        
        return 0
    
    except TicketLoadError as e:
        logger.error(f"Failed to load ticket: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    except CategoriesLoadError as e:
        logger.error(f"Failed to load categories: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        logger.exception("An unexpected error occurred")
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())