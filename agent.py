import json
import os
import time

import requests
from dotenv import load_dotenv

from tools import TOOLS
from validator import validate_tool_arguments


load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")
URL = "https://api.groq.com/openai/v1/chat/completions"

MAX_STEPS = 6


def call_model(messages, tools, max_tokens=500):
    response = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": max_tokens
        },
        timeout=60
    )

    response.raise_for_status()
    return response.json()


def run_tool_call(tool_call):
    try:
        tool_name = tool_call["function"]["name"]

        if tool_name not in TOOLS:
            return f"Unknown tool: {tool_name}"

        raw_arguments = tool_call["function"].get("arguments", "{}")

        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError:
            return "Invalid JSON in tool arguments"

        error = validate_tool_arguments(tool_name, arguments)

        if error:
            return error

        return str(TOOLS[tool_name](**arguments))

    except Exception as e:
        return f"Tool execution error: {e}"


def build_tool_definitions():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_subject_schedule",
                "description": (
                    "Get the study schedule for a subject."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string"
                        }
                    },
                    "required": ["subject"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_study_hours",
                "description": (
                    "Calculate total available study hours."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "available_hours": {
                            "type": "number"
                        },
                        "days": {
                            "type": "integer",
                            "enum": [1, 2, 3, 4, 5, 6, 7]
                        }
                    },
                    "required": ["available_hours", "days"],
                    "additionalProperties": False
                }
            }
        }
    ]


def run_agent(user_question):
    messages = [
        {
            "role": "system",
            "content": (
               "You are a student study assistant. "
               "Use tools when they are useful. "
               "Use all required independent tools in the same response when possible. "
               "Never invent tool results."
)
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    tools = build_tool_definitions()
    previous_calls = set()

    for step in range(1, MAX_STEPS + 1):
        print(f"\n--- Step {step} ---")

        max_tokens = 500

        for retry in range(2):
            data = call_model(
                messages,
                tools,
                max_tokens=max_tokens
            )

            choice = data["choices"][0]
            finish_reason = choice.get("finish_reason")
            message = choice["message"]

            if finish_reason == "length":
                if retry == 0:
                    print("finish_reason=length -> retrying")
                    max_tokens = 1000
                    continue

            break

        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            print("Final answer:")
            print(message.get("content", ""))
            return

        messages.append(message)

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            raw_args = tool_call["function"].get("arguments", "{}")

            call_key = f"{tool_name}:{raw_args}"

            if call_key in previous_calls:
                print("Repeated identical call detected. Stopping.")
                return

            previous_calls.add(call_key)

            print(f"Tool call: {tool_name}")
            print(f"Arguments: {raw_args}")

            result = run_tool_call(tool_call)

            print(f"Tool result: {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result
                }
            )

    print("Maximum number of steps reached.")


if __name__ == "__main__":
    question = input("Ask your study assistant: ")
    run_agent(question)