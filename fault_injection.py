from agent import run_tool_call


faults = [
    {
        "name": "Invalid JSON",
        "call": {
            "function": {
                "name": "get_subject_schedule",
                "arguments": '{"subject":'
            }
        }
    },
    {
        "name": "Unknown tool",
        "call": {
            "function": {
                "name": "unknown_tool",
                "arguments": "{}"
            }
        }
    },
    {
        "name": "Missing argument",
        "call": {
            "function": {
                "name": "get_subject_schedule",
                "arguments": "{}"
            }
        }
    },
    {
        "name": "Wrong type",
        "call": {
            "function": {
                "name": "calculate_study_hours",
                "arguments": '{"available_hours":"five","days":2}'
            }
        }
    },
    {
        "name": "Value outside enum",
        "call": {
            "function": {
                "name": "calculate_study_hours",
                "arguments": '{"available_hours":3,"days":10}'
            }
        }
    },
    {
        "name": "Invented argument",
        "call": {
            "function": {
                "name": "get_subject_schedule",
                "arguments": '{"subject":"Python","teacher":"John"}'
            }
        }
    },
    {
        "name": "Negative hours",
        "call": {
            "function": {
                "name": "calculate_study_hours",
                "arguments": '{"available_hours":-5,"days":2}'
            }
        }
    },
    {
        "name": "Wrong subject value type",
        "call": {
            "function": {
                "name": "get_subject_schedule",
                "arguments": '{"subject":123}'
            }
        }
    }
]


print("=== Fault Injection Test ===")

for i, fault in enumerate(faults, 1):
    result = run_tool_call(fault["call"])

    print(f"\n{i}. {fault['name']}")
    print(f"Returned message: {result}")