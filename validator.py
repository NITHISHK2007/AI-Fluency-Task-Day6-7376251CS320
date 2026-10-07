from tools import SCHEMAS


def validate_tool_arguments(tool_name, arguments):
    if tool_name not in SCHEMAS:
        return f"Unknown tool: {tool_name}"

    schema = SCHEMAS[tool_name]

    # Check required arguments
    for name in schema["required"]:
        if name not in arguments:
            return f"Missing required argument: {name}"

    # Check extra arguments
    allowed = set(schema["properties"].keys())
    extra = set(arguments.keys()) - allowed

    if extra:
        return f"Invented extra argument: {', '.join(extra)}"

    # Check argument types
    for name, rules in schema["properties"].items():
        if name not in arguments:
            continue

        value = arguments[name]
        expected = rules["type"]

        if expected == "string" and not isinstance(value, str):
            return f"Wrong type for {name}: expected string"

        if expected == "number" and (
            not isinstance(value, (int, float)) or isinstance(value, bool)
        ):
            return f"Wrong type for {name}: expected number"

        if expected == "integer" and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            return f"Wrong type for {name}: expected integer"

        # Check enum
        if "enum" in rules and value not in rules["enum"]:
            return (
                f"Value outside allowed list for {name}: "
                f"{value}. Expected one of {rules['enum']}"
            )

    return None