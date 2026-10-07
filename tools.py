from typing import Dict


SCHEMAS = {
    "get_subject_schedule": {
        "description": "Get the study schedule for a subject.",
        "properties": {
            "subject": {
                "type": "string"
            }
        },
        "required": ["subject"],
        "additionalProperties": False,
        "strict": True
    },
    "calculate_study_hours": {
        "description": "Calculate how many hours are available for studying.",
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
        "additionalProperties": False,
        "strict": True
    }
}


SCHEDULES = {
    "python": "Practice arrays, strings and basic problem solving.",
    "dsa": "Practice stacks, queues, linked lists and algorithms.",
    "dbms": "Revise SQL, normalization and database concepts."
}


def get_subject_schedule(subject: str) -> str:
    return SCHEDULES.get(
        subject.lower(),
        "No schedule found for this subject."
    )


def calculate_study_hours(available_hours: float, days: int) -> str:
    total = available_hours * days
    return f"Total available study time: {total:.1f} hours"


TOOLS = {
    "get_subject_schedule": get_subject_schedule,
    "calculate_study_hours": calculate_study_hours
}
