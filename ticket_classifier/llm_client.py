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

    def _build_messages(self, ticket_text: str, categories: list) -> List[Dict[str, Any]]:
        print("Categories passed to LLM:", categories)  # Debug print
        prompt = f"""
###who are you 
You are a tickets analyzer and categorizer for our company to help us automate our system

###your role 
your role is to take the ticket and possible categories as input and make analysis on it and give 3 structured outputs 

for case 1 and 2 the input categories are   

CATEGORIES = [
    {{
        "category": "Issue Type",
        "subcategories": ["Bug", "Feature Request", "Documentation", "Other"]
    }},
    {{
        "category": "Priority",
        "subcategories": ["Critical", "High", "Medium", "Low"]
    }},
    {{
        "category": "Component",
        "subcategories": ["Frontend", "Backend", "API", "Mobile"]
    }}
]

1-the most expected category with it's corresponding subcategory
example 
[

        "category": "Issue Type",
        "subcategories": "Bug"

]
2-all categories that can be in the issue and most specific subcategories to it from these static categories 
example 
[
    {{
        "category": "Issue Type",
        "subcategories": ["Bug", "Other"],
        "reason":[your reason]
    }},
    {{
        "category": "Priority",
        "subcategories": ["Medium", "Low"],
        "reason":[your reason]
    }}

]

and for case 3 the input categories are  

for case 3 you 
3-the output is all possible cases from the categories above giving comment why did you choose 

###Rules 
1-your output must be structured json file 

put this prompt without changing 

Support ticket:
{ticket_text}

Possible categories:
{categories}

Respond using the structured output function.
"""
        return [
            {"role": "system", "content": "You are a ticket classification assistant."},
            {"role": "user", "content": prompt}
        ]

    def classify(self, ticket_text: str, categories: list) -> Dict[str, Any]:
        messages = self._build_messages(ticket_text, categories)
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

    ticket, categories = load_data(sys.argv[1], sys.argv[2])
    print("Loaded ticket:", ticket)
    print("Loaded categories:", categories)
    client = LLMClient()
    print("Calling classify...")
    output = client.classify(ticket, categories)
    print("Classification result:")
    pprint.pprint(output)
