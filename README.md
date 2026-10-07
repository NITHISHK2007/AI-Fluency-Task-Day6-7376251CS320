# Day 6 Task – Reliable Tool Calling

## Scenario

**Student Study Planner**

This project demonstrates reliable tool calling using an OpenAI-compatible API.

The assistant uses two tools:

* `get_subject_schedule`
* `calculate_study_hours`

## Project Files

* `tools.py` – Tool implementations and JSON schemas
* `validator.py` – Validates tool names and arguments
* `agent.py` – Reliable tool-calling agent loop
* `fault_injection.py` – Tests deliberately broken tool calls
* `structured_output.py` – Compares normal output, JSON mode and schema mode
* `analysis.md` – Complete analysis and observations
* `outputs/` – Test output screenshots

## Reliability Features

The project demonstrates:

* JSON Schema validation
* Required arguments
* Enum validation
* `additionalProperties: false`
* Tool-call error handling
* Retry after `finish_reason=length`
* Repeated-call protection
* Fault injection
* Structured outputs

## Key Observation

Schema validation catches many structural tool-call errors, but it does not automatically detect semantic errors such as negative study hours. Additional application-level validation is required for such cases.

## Structured Output

Three approaches were tested:

1. No constraint
2. JSON mode
3. Schema mode

Schema mode successfully produced a valid, parseable structured response in the test.

## Note

API credentials are stored in `.env` and are excluded from Git using `.gitignore`.

