import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")
URL = "https://api.groq.com/openai/v1/chat/completions"


def call_api(messages, response_format=None):
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 300
    }

    if response_format:
        payload["response_format"] = response_format

    response = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )

    if not response.ok:
        return f"ERROR: {response.status_code} - {response.text}"

    return response.json()


question = (
    "Extract the student details from this sentence: "
    "'Nithish studies CSE and has 2 hours available for study.' "
    "Return the name, department and available hours."
)

messages = [
    {
        "role": "user",
        "content": question
    }
]


print("=== 1. No Constraint ===")

result = call_api(messages)

if isinstance(result, str):
    print(result)
else:
    raw = result["choices"][0]["message"].get("content", "")
    print("Raw reply:")
    print(raw)

    try:
        print("Parsed result:")
        print(json.loads(raw))
    except json.JSONDecodeError:
        print("Could not parse as JSON.")


print("\n=== 2. JSON Mode ===")

result = call_api(
    messages,
    {
        "type": "json_object"
    }
)

if isinstance(result, str):
    print(result)
else:
    raw = result["choices"][0]["message"].get("content", "")
    print("Raw reply:")
    print(raw)

    try:
        print("Parsed result:")
        print(json.loads(raw))
    except json.JSONDecodeError:
        print("Could not parse as JSON.")


print("\n=== 3. Schema Mode ===")

schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "student_details",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "department": {
                    "type": "string"
                },
                "available_hours": {
                    "type": "number"
                }
            },
            "required": [
                "name",
                "department",
                "available_hours"
            ],
            "additionalProperties": False
        }
    }
}

result = call_api(messages, schema)

if isinstance(result, str):
    print(result)
else:
    raw = result["choices"][0]["message"].get("content", "")
    print("Raw reply:")
    print(raw)

    try:
        print("Parsed result:")
        print(json.loads(raw))
    except json.JSONDecodeError:
        print("Could not parse as JSON.")