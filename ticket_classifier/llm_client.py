# src/ticket_classifier/llm_client.py

import openai
from openai import OpenAI
import json
from typing import List, Dict, Any
from ticket_classifier.config import OPENAI_API_KEY, MODEL, TIMEOUT_SECONDS

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL  # should be set to "gpt-4.1" in .env
        self.timeout = TIMEOUT_SECONDS
        self.function_schema = {
            "name": "classify_ticket",
            "description": "Return structured classification for cases 1, 2, and 3",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_1": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "subcategory": {"type": "string"}
                        },
                        "required": ["category", "subcategory"]
                    },
                    "case_2": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string"},
                                "subcategories": {
                                    "type": "array", "items": {"type": "string"}
                                },
                                "reason": {
                                    "type": "array", "items": {"type": "string"}
                                }
                            },
                            "required": ["category", "subcategories", "reason"]
                        }
                    },
                    "case_3": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string"},
                                "subcategories": {
                                    "type": "array", "items": {"type": "string"}
                                },
                                "comment": {"type": "string"}
                            },
                            "required": ["category", "subcategories", "comment"]
                        }
                    }
                },
                "required": ["case_1", "case_2", "case_3"]
            }
        }

    def _build_messages(self, ticket_text: str, category_paths: List[List[str]]) -> List[Dict[str, Any]]:
        paths_str = "\n".join([" > ".join(path) for path in category_paths])

        prompt = f"""
Part 1: Single Category Classification (Static)
First, imagine the requirements are simple. The program only needs to find the primary issue type in a ticket.
-	Task: Write a function or script that analyzes the issue and identifies the single most prominent category and its corresponding subcategory.  
-	Categories: For this part, assume a fixed, hard-coded list of categories:
-	Issue Type: (Subcategories: Bug, Feature Request, Documentation, Other)
-	Priority: (Subcategories: Critical, High, Medium, Low)
Part 2: Multi-Issue Extraction
Support tickets often contain multiple aspects that need to be classified. Your program must be able to capture all of them.

-	Task: Evolve your script to extract a list of all categories and their most specific subcategories present in the ticket description.  
-	Example: For the sample support ticket provided, your program should identify multiple aspects such as "Issue Type", "Priority", and "Component".

Part 3: Dynamic and Nested Category Loading
Our clients want to manage their own categories without needing a developer to update the code. Your script must be flexible enough to handle this.
-	Task: Adapt your script so that it no longer uses a hard-coded list. Instead, it must read the categories from the provided categories.json file at runtime. The script must be able to parse the nested structure of this file and handle varying levels of depth

Support ticket:
{ticket_text}

Possible category paths:
{paths_str}

Respond using the structured output function.
"""
        return [
            {"role": "system", "content": "You are a ticket classification assistant."},
            {"role": "user", "content": prompt}
        ]

    def classify(self, ticket_text: str, category_paths: List[List[str]]) -> Dict[str, Any]:
        messages = self._build_messages(ticket_text, category_paths)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=[self.function_schema],
            function_call={"name": "classify_ticket"},
            temperature=0.0,
            timeout=self.timeout
        )
        arguments = response.choices[0].message.function_call.arguments
        return json.loads(arguments)

if __name__ == "__main__":
    import sys, pprint
    from ticket_classifier.data_loader import load_data

    if len(sys.argv) != 3:
        print("Usage: python -m ticket_classifier.llm_client <ticket.txt> <categories.json>")
        sys.exit(1)

    ticket, raw_cats = load_data(sys.argv[1], sys.argv[2])
    print("Loaded ticket:", ticket)
    print("Loaded categories:", raw_cats)
    # If you need flattened paths, implement flatten_category_paths here or in data_loader.py
    # For now, pass raw_cats directly
    client = LLMClient()
    print("Calling classify...")
    output = client.classify(ticket, raw_cats)
    print("Classification result:")
    pprint.pprint(output)
