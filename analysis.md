# Day 6 Task – Reliable Tool Calling

## 1. Scenario

### Scenario: Student Study Planner

This project is designed for a student study planner. The assistant can use two tools:

1. `get_subject_schedule` – returns a study schedule for a selected subject.
2. `calculate_study_hours` – calculates the total available study time from daily study hours and number of days.

The purpose is to demonstrate reliable tool calling, schema validation, retry handling, fault injection, and structured outputs.

---

## 2. Key Concepts

### 2.1 Chat Completions and Tool Calls

An OpenAI-compatible Chat Completions API can return normal assistant content or request tool calls. When a tool call is returned, the assistant message can contain tool-call information instead of normal text content.

The tool-calling process used in this project is:

1. Send the user request and tool definitions to the model.
2. Inspect the model response for tool calls.
3. Parse the tool name and arguments.
4. Validate the arguments against the schema.
5. Execute the tool if validation succeeds.
6. Return the tool result to the model and continue the loop.
7. Stop when the model produces a final answer.

### 2.2 Tool Schema

Each tool definition contains a description and JSON Schema information such as:

* `properties`
* `required`
* `enum`
* `additionalProperties`
* `strict`

The schemas in this project are stored in one `SCHEMAS` dictionary in `tools.py`. The same schemas are used by the model and by the validator.

### 2.3 Why Tool Calls Cannot Be Fully Trusted

A model-generated tool call can contain:

* Invalid JSON
* An unknown tool name
* Missing arguments
* Wrong argument types
* Invalid enum values
* Invented extra arguments
* Truncated arguments
* Repeated tool calls
* Semantically invalid values

Therefore, the application validates tool calls before executing them.

### 2.4 JSON Mode and Schema Mode

JSON mode attempts to produce JSON-formatted output, while schema-based structured output constrains the response to a specified structure.

In this implementation, the JSON mode request returned an API error because the request messages did not contain the word `json`. Schema mode successfully returned valid JSON matching the expected fields.

---

## 3. Tool Definitions

The project contains two tools.

### Tool 1: get_subject_schedule

Input:

* `subject`: string

Supported subjects include Python, DSA and DBMS.

### Tool 2: calculate_study_hours

Inputs:

* `available_hours`: number
* `days`: integer
* `days` uses an enum containing values from 1 to 7.

Both schemas use `required` and `additionalProperties: false`.

---

## 4. Validator

The validator checks the model-generated tool call before execution.

It detects:

* Unknown tool
* Missing required argument
* Invented extra argument
* Wrong argument type
* Invalid enum value
* Invalid JSON

The validator returns errors as strings so that the agent loop can handle failures without crashing.

---

## 5. Agent Loop

The agent loop performs the following operations:

1. Sends the conversation and tool definitions to the model.
2. Checks the `finish_reason`.
3. If the response is truncated because of `length`, it retries with a larger `max_tokens` value.
4. Parses tool calls.
5. Validates every tool call.
6. Executes valid tools.
7. Sends one tool result for each tool call.
8. Detects repeated identical calls.
9. Stops after a maximum number of steps.

The implementation therefore does not blindly execute model-generated tool arguments.

---

## 6. Fault Injection Results

Eight deliberately broken tool calls were tested.

| Test | Fault                    | Result     |
| ---- | ------------------------ | ---------- |
| 1    | Invalid JSON             | Caught     |
| 2    | Unknown tool             | Caught     |
| 3    | Missing argument         | Caught     |
| 4    | Wrong type               | Caught     |
| 5    | Invalid enum value       | Caught     |
| 6    | Invented argument        | Caught     |
| 7    | Negative study hours     | Not caught |
| 8    | Wrong subject value type | Caught     |

The negative-hours case is an important limitation. The schema correctly identifies `-5` as a number, but it does not define a semantic rule that study hours must be positive. Therefore, the tool executed and produced `-10.0 hours`.

This demonstrates that schema validation prevents many structural errors but does not automatically prevent every logically invalid value.

---

## 7. Agent Behaviour Tests

### 7.1 Single Tool

Question:

"How many study hours are available if I can study 3 hours per day for 2 days?"

The model called `calculate_study_hours` with:

```json
{"available_hours":3,"days":2}
```

The tool returned 6.0 hours and the agent produced the final answer.

### 7.2 Two Tools

Question:

"Give me the Python study schedule and calculate my total study time if I study 2 hours per day for 3 days."

The model used both tools:

1. `get_subject_schedule`
2. `calculate_study_hours`

The calls were made sequentially rather than in one parallel response.

The final answer correctly combined the Python schedule and the calculated total of 6 hours.

### 7.3 Invalid Value Temptation

Question:

"Calculate my study time if I study -5 hours per day for 3 days."

The model generated:

```json
{"available_hours":-5,"days":3}
```

The validator accepted the value because `-5` is a valid number type. The tool returned `-15.0 hours`.

The final response recognized that the negative value was inconsistent. This shows why semantic validation should be added for values such as study hours.

### 7.4 No Tool Required

Question:

"What is Python?"

No tool was required. The model answered directly.

The first response reached `finish_reason=length`, so the retry logic increased the token limit and successfully produced the final answer.

---

## 8. Structured Output Results

The same extraction task was tested in three ways.

### No Constraint

The model returned Markdown-formatted student details. JSON parsing failed because the response was not valid JSON.

### JSON Mode

The request returned an API error:

```text
'messages' must contain the word 'json' in some form, to use 'response_format' of type 'json_object'.
```

This demonstrates that the API setup has an additional requirement for JSON mode.

### Schema Mode

The model returned:

```json
{"name":"Nithish","department":"CSE","available_hours":2}
```

The response was successfully parsed as JSON.

Schema mode therefore produced the most reliable structured result in this test.

---

## 9. Before and After Reliability Guards

### Before Guards

Without validation, a model-generated tool call could directly reach the tool implementation. Invalid JSON, unknown tools, missing arguments, wrong types and invalid enum values could cause incorrect execution or failures.

### After Guards

With schema validation and the agent loop:

* Invalid JSON is rejected.
* Unknown tools are rejected.
* Missing arguments are rejected.
* Wrong types are rejected.
* Invalid enum values are rejected.
* Invented arguments are rejected.
* Truncated model responses can trigger a retry.
* Repeated identical calls can be stopped.
* Valid calls are executed only after validation.

However, semantic constraints such as "study hours must be positive" still need explicit validation.

---

## 10. Suitability

This approach is suitable for a student study planner because the assistant can safely connect natural-language requests to small deterministic tools.

Tool calling is useful when the assistant needs to perform an action or calculation. Structured outputs are more suitable when the main requirement is extracting information into a predictable format.

For this scenario, validation is important because the model should not be trusted to always produce correct tool names or arguments.

---

## 11. Conclusion

This project demonstrated reliable tool calling using an OpenAI-compatible API. Two study-planning tools were created with JSON Schema definitions and validated before execution.

The fault-injection tests showed that validation can catch several common tool-call failures. The negative-hours test also showed that schemas alone cannot guarantee semantic correctness.

The agent loop handled tool execution, multiple tool calls, retry after a `length` finish reason, and repeated-call protection. Structured-output testing showed that schema-based output produced a valid and parseable result.

Overall, reliable tool calling requires more than simply giving tools to an LLM. Tool schemas, validation, controlled execution, retries, failure handling, and structured outputs are all important for making an agent more dependable.
