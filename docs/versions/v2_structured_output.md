# V2 - Prompting + Structured Output

## Version Goal
V2 turns the basic chat API from V1 into a structured-output workflow.

Instead of trusting the LLM to return free-form text, we ask it for a predictable JSON response, validate that JSON with Pydantic, and expose it through a dedicated API endpoint.

## What We Built
- A structured response schema for LLM answers.
- A versioned structured prompt template.
- A parser that converts raw LLM text into a validated Pydantic model.
- A structured LLM service that connects prompting, provider calls, and parsing.
- Retry once when the model returns invalid structured output.
- A fallback structured response when retry also fails.
- A new `POST /chat/structured` endpoint.
- Unit and integration tests for each layer.
- A cleaner test directory split into `unit/` and `integration/`.

## Why We Built It
LLMs are naturally flexible, but backend APIs need predictable contracts.

V2 introduces a controlled response shape so future features can safely depend on fields like `confidence`, `reasoning_summary`, `next_action`, and `status`.

This is important because later versions will analyze files, datasets, and documents. Those features should not have to parse random paragraphs every time the LLM responds.

## Workflow
```text
Client request
-> POST /chat/structured
-> ChatRequest validation
-> build_structured_prompt()
-> generate_answer()
-> raw LLM JSON text
-> parse_structured_response()
-> StructuredLLMResponse validation
-> retry once if parsing/validation fails
-> fallback structured response if retry still fails
-> structured API response
```

## Files Added
- `app/schemas/structured.py`
- `app/prompts/structured_v2.py`
- `app/services/structured_parser.py`
- `app/services/structured_llm_service.py`
- `tests/unit/test_structured_schemas.py`
- `tests/unit/test_structured_prompt.py`
- `tests/unit/test_structured_parser.py`
- `tests/unit/test_structured_llm_service.py`

## Files Updated
- `app/api/routes_chat.py`
- `tests/integration/test_chat_endpoint.py`
- `README.md`
- `docs/project_report.md`

## Design Decisions

### Separate Schema From Prompt
The schema lives in `app/schemas/structured.py`, while the prompt lives in `app/prompts/structured_v2.py`.

This keeps the API contract separate from prompt wording. The schema defines what the backend accepts. The prompt is only one way to guide the model toward that shape.

### Use Literal Values For Controlled Fields
`confidence` is restricted to:

```text
low | medium | high
```

`status` is restricted to:

```text
success | failed
```

This prevents vague values like `certain`, `ok`, or `maybe` from entering the backend contract.

### Validate LLM Output After Generation
The LLM is asked to return JSON, but we do not blindly trust it.

`parse_structured_response()` first checks whether the output is valid JSON, then checks whether it matches `StructuredLLMResponse`.

### Retry And Fallback For Invalid Output
The structured service retries once when the LLM returns invalid JSON or JSON that does not match the schema.

If the retry still fails, it returns a valid fallback `StructuredLLMResponse` with:

```text
status = failed
confidence = low
```

This means the API still returns a predictable response shape even when the model fails the structured-output contract.

### Convert Provider Errors Into Service Errors
The structured service still converts provider failures, such as timeout or API failure, into `StructuredLLMServiceError`.

This keeps the API route clean. The route does not need to know provider-specific error details.

### Mock LLM Calls In Tests
Tests patch the service functions instead of calling the real provider.

This makes tests fast, repeatable, and safe to run without spending API credits or depending on network availability.

## Endpoint
```text
POST /chat/structured
```

Request:

```json
{
  "message": "Explain missing values in a dataset in simple words."
}
```

Expected response shape:

```json
{
  "answer": "Missing values are empty entries in a dataset.",
  "confidence": "high",
  "reasoning_summary": "The user asked for a simple explanation.",
  "next_action": "No tool required.",
  "prompt_version": "v2.1",
  "status": "success"
}
```

## Tests Performed
- Unit tested structured schema validation.
- Unit tested prompt construction.
- Unit tested JSON parsing and schema validation.
- Unit tested structured LLM service success, provider failure, retry, and fallback paths.
- Integration tested `/chat/structured` success response.
- Integration tested `/chat/structured` controlled error response.
- Integration tested that fallback structured responses can be returned.
- Manually tested `/chat/structured` against the real configured LLM provider.

Latest full test result:

```text
27 passed
```

## What I Learned
- Prompting is not enough; backend validation is still required.
- Structured output is a contract between the LLM and the backend.
- Pydantic can protect the app from invalid model responses.
- Retry/fallback logic makes structured output safer for API users.
- Mocking lets us test LLM-powered code without calling the LLM.
- Unit tests check individual layers, while integration tests check whether the API pieces work together.
- A service layer keeps routes small and easier to explain.

## Interview Explanation
In V2, I added structured LLM output to the FastAPI backend. I created a Pydantic response schema, a versioned prompt template, a parser for raw LLM JSON, and a structured service that connects the prompt, LLM call, validation, retry, and fallback behavior. I exposed this through `POST /chat/structured` and tested the workflow with both unit and integration tests. This made the API more reliable because the backend no longer depends on free-form LLM text.

## Commit Points
- `v2: add structured response schemas`
- `v2: add structured prompt template`
- `v2: organize tests by test type`
- `v2: add structured output parser`
- `v2: add structured LLM service`
- `v2: add structured chat endpoint`
- `v2: add retry and fallback for structured output`
- `v2: document structured output workflow`
