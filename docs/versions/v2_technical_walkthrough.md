# V2 Technical Walkthrough

This document explains the V2 structured-output implementation file by file. The goal is to make the code easy to revise, debug, and explain in interviews.

V2 builds on V1. V1 returned free-form chat text. V2 adds a second path where the model response must come back as validated JSON.

## 1. Mental Model

```text
Client
  sends POST /chat/structured

routes_chat.py
  receives HTTP request
  delegates work to structured service

structured_llm_service.py
  builds structured prompt
  calls existing LLM service
  sends raw output to parser

structured_v2.py
  owns the prompt template and prompt version

llm_service.py
  talks to the configured LLM provider

structured_parser.py
  converts raw JSON text into a Pydantic model

structured.py
  defines the response contract

FastAPI
  serializes the validated response back to the client
```

## 2. `app/schemas/structured.py`

### Purpose
`structured.py` defines the contract for structured LLM responses.

This file answers: "What shape must the LLM response have before our backend accepts it?"

### Code
```python
from typing import Literal

from pydantic import BaseModel, field_validator


ConfidenceLevel = Literal["low", "medium", "high"]
Status = Literal["success", "failed"]


class StructuredLLMResponse(BaseModel):
    answer: str
    confidence: ConfidenceLevel
    reasoning_summary: str
    next_action: str
    prompt_version: str
    status: Status

    @field_validator("answer", "reasoning_summary", "next_action", "prompt_version", "status")
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Field must not be empty.")

        return cleaned_value
```

### Explanation
```python
from typing import Literal
```
Imports `Literal`, which restricts a field to exact allowed values.

```python
from pydantic import BaseModel, field_validator
```
Imports Pydantic's model base class and custom validator decorator.

```python
ConfidenceLevel = Literal["low", "medium", "high"]
```
Defines the only allowed confidence values. This prevents random values like `certain`, `maybe`, or `very high`.

```python
Status = Literal["success", "failed"]
```
Defines the only allowed response status values.

```python
class StructuredLLMResponse(BaseModel):
```
Creates a Pydantic model for the structured response.

```python
answer: str
confidence: ConfidenceLevel
reasoning_summary: str
next_action: str
prompt_version: str
status: Status
```
Defines the exact response fields that the API will return.

```python
@field_validator("answer", "reasoning_summary", "next_action", "prompt_version", "status")
```
Runs the same validation logic on multiple text fields.

```python
cleaned_value = value.strip()
```
Trims whitespace.

```python
if not cleaned_value:
    raise ValueError("Field must not be empty.")
```
Rejects blank strings.

```python
return cleaned_value
```
Stores the cleaned value in the final model.

### Design Decision
The schema is strict because LLM output should be treated like external input. Even if the prompt asks for good JSON, the backend still validates it.

### Interview Explanation
I used a Pydantic model to define the structured LLM response contract. `Literal` restricts fields like confidence and status, while validators prevent blank text. This keeps the API response predictable and protects the backend from invalid model output.

## 3. `app/prompts/structured_v2.py`

### Purpose
`structured_v2.py` owns the prompt instructions for structured output.

This file answers: "How do we ask the LLM to produce the response shape our backend expects?"

### Code
```python
STRUCTURED_PROMPT_VERSION = "v2.1"

STRUCTURED_SYSTEM_PROMPT = """
You are InsightAgent, an AI backend assistant for data and document analysis.

Return only valid JSON matching this schema:
{
  "answer": string,
  "confidence": "low" | "medium" | "high",
  "reasoning_summary": string,
  "next_action": string,
  "prompt_version": string,
  "status": "success" | "failed"
}

Rules:
- Be concise and accurate.
- Do not invent facts.
- If unsure, use "confidence": "low".
- Keep reasoning_summary short and safe.
- Do not reveal hidden chain-of-thought.
- Do not include markdown, code fences, or text outside JSON.
- Use prompt_version: "v2.1".
""".strip()


def build_structured_prompt(message: str) -> str:
    return f"{STRUCTURED_SYSTEM_PROMPT}\n\nUser message:\n{message}"
```

### Explanation
```python
STRUCTURED_PROMPT_VERSION = "v2.1"
```
Stores the prompt version in one place.

```python
STRUCTURED_SYSTEM_PROMPT = """...""".strip()
```
Defines the instruction block sent to the LLM.

```text
Return only valid JSON matching this schema
```
Tells the LLM not to return normal prose.

```text
Do not include markdown, code fences, or text outside JSON.
```
Prevents responses like:

```text
Here is the JSON:
```json
...
```
```

Those responses look nice to humans but break machine parsing.

```text
Do not reveal hidden chain-of-thought.
```
Keeps `reasoning_summary` short and safe instead of asking for private reasoning.

```python
def build_structured_prompt(message: str) -> str:
```
Creates the final prompt for one user message.

```python
return f"{STRUCTURED_SYSTEM_PROMPT}\n\nUser message:\n{message}"
```
Combines system-style instructions with the user input.

### Design Decision
The prompt is separate from the schema because wording changes should not be mixed with API contract changes.

### Interview Explanation
I created a versioned structured prompt so LLM behavior can be tracked over time. The prompt asks for JSON only, defines the required fields, and includes safety rules like avoiding hidden chain-of-thought. The version field helps debug future prompt changes.

## 4. `app/services/structured_parser.py`

### Purpose
`structured_parser.py` converts raw LLM text into a validated `StructuredLLMResponse`.

This file answers: "Did the LLM actually return valid JSON matching our schema?"

### Code
```python
import json

from pydantic import ValidationError

from app.schemas.structured import StructuredLLMResponse


class StructuredOutputParseError(Exception):
    pass


def parse_structured_response(raw_output: str) -> StructuredLLMResponse:
    try:
        parsed_output = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise StructuredOutputParseError("LLM output was not valid JSON.") from exc

    try:
        return StructuredLLMResponse.model_validate(parsed_output)
    except ValidationError as exc:
        raise StructuredOutputParseError("LLM output did not match the expected schema.") from exc
```

### Explanation
```python
import json
```
Imports Python's standard JSON parser.

```python
from pydantic import ValidationError
```
Imports the error type raised when a Pydantic model rejects input.

```python
class StructuredOutputParseError(Exception):
    pass
```
Defines an app-specific parser error.

```python
parsed_output = json.loads(raw_output)
```
Converts the LLM string into a Python object.

```python
except json.JSONDecodeError as exc:
```
Catches invalid JSON.

```python
raise StructuredOutputParseError("LLM output was not valid JSON.") from exc
```
Raises a clean app-level error while preserving the original exception context.

```python
return StructuredLLMResponse.model_validate(parsed_output)
```
Validates the parsed JSON against the Pydantic schema.

```python
except ValidationError as exc:
```
Catches cases where JSON is valid but the fields are wrong.

### Design Decision
Parsing has two stages:
- JSON syntax validation
- Pydantic schema validation

This lets us distinguish between "not JSON" and "JSON, but wrong shape."

### Interview Explanation
I added a parser layer because prompt instructions alone are not reliable enough. The parser first checks whether the LLM output is valid JSON, then validates it against the Pydantic response model. Any failure becomes a controlled parser error.

## 5. `app/services/structured_llm_service.py`

### Purpose
`structured_llm_service.py` is the business-flow layer for structured chat.

This file answers: "How do prompting, provider call, and parsing work together as one feature?"

### Code
```python
from app.prompts.structured_v2 import build_structured_prompt
from app.schemas.structured import StructuredLLMResponse
from app.services.llm_service import LLMServiceError, generate_answer
from app.services.structured_parser import (
    StructuredOutputParseError,
    parse_structured_response,
)


MAX_STRUCTURED_OUTPUT_ATTEMPTS = 2


class StructuredLLMServiceError(Exception):
    pass


def build_structured_fallback_response() -> StructuredLLMResponse:
    return StructuredLLMResponse(
        answer="I could not generate a valid structured response.",
        confidence="low",
        reasoning_summary="The model output failed validation.",
        next_action="Please retry or simplify the question.",
        prompt_version="v2.1",
        status="failed",
    )


def generate_structured_answer(message: str) -> StructuredLLMResponse:
    prompt = build_structured_prompt(message)

    for _ in range(MAX_STRUCTURED_OUTPUT_ATTEMPTS):
        try:
            raw_output = generate_answer(prompt)
        except LLMServiceError as exc:
            raise StructuredLLMServiceError(str(exc)) from exc

        try:
            return parse_structured_response(raw_output)
        except StructuredOutputParseError:
            continue

    return build_structured_fallback_response()
```

### Explanation
```python
from app.prompts.structured_v2 import build_structured_prompt
```
Imports the prompt builder.

```python
from app.schemas.structured import StructuredLLMResponse
```
Imports the return type for the service.

```python
from app.services.llm_service import LLMServiceError, generate_answer
```
Reuses the existing V1 LLM provider wrapper.

```python
from app.services.structured_parser import ...
```
Imports the parser and parser error.

```python
class StructuredLLMServiceError(Exception):
    pass
```
Defines one high-level error for this structured feature.

```python
def build_structured_fallback_response() -> StructuredLLMResponse:
```
Builds a valid failed response when the model cannot produce valid structured output after retry.

```python
prompt = build_structured_prompt(message)
```
Turns the user's message into a structured-output prompt.

```python
for _ in range(MAX_STRUCTURED_OUTPUT_ATTEMPTS):
```
Allows the service to try the structured-output generation flow twice.

```python
raw_output = generate_answer(prompt)
```
Sends the structured prompt to the configured LLM provider.

```python
except LLMServiceError as exc:
```
Catches provider/service failures from the existing LLM layer.

```python
return parse_structured_response(raw_output)
```
Validates the model output and returns a typed response.

```python
except StructuredOutputParseError:
```
Catches parser failures and continues to the next attempt.

```python
return build_structured_fallback_response()
```
Returns a valid fallback response when both attempts fail validation.

### Design Decision
This service turns multiple lower-level operations into one clean function for the route:

```text
message -> prompt -> LLM raw output -> parsed response -> retry/fallback if needed
```

The route does not need to know how prompts or parsing work.

### Interview Explanation
I created a structured service to coordinate the full structured-output flow. It builds the prompt, calls the existing LLM service, parses the response, retries once if parsing or validation fails, and returns a safe fallback response if the retry still fails. Provider-level failures are still converted into one service-level error. This keeps the API route simple while making invalid model output safer.

## 6. `app/api/routes_chat.py`

### Purpose
In V2, `routes_chat.py` still contains the original `/chat` endpoint, and now also exposes `/chat/structured`.

This file answers: "How does the user call the structured-output feature through HTTP?"

### V2 Code
```python
from app.schemas.structured import StructuredLLMResponse
from app.services.structured_llm_service import (
    StructuredLLMServiceError,
    generate_structured_answer,
)


@router.post("/chat/structured", response_model=StructuredLLMResponse)
def structured_chat(request: ChatRequest) -> StructuredLLMResponse:
    try:
        return generate_structured_answer(request.message)
    except StructuredLLMServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "STRUCTURED_LLM_SERVICE_ERROR",
                    "message": str(exc),
                }
            },
        ) from exc
```

### Explanation
```python
from app.schemas.structured import StructuredLLMResponse
```
Imports the response model for the structured endpoint.

```python
from app.services.structured_llm_service import ...
```
Imports the structured service function and its controlled error.

```python
@router.post("/chat/structured", response_model=StructuredLLMResponse)
```
Registers a POST endpoint and tells FastAPI the response shape.

```python
def structured_chat(request: ChatRequest) -> StructuredLLMResponse:
```
Uses the existing `ChatRequest` schema because the incoming request body is still just a user message.

```python
return generate_structured_answer(request.message)
```
Delegates the structured flow to the service layer.

```python
except StructuredLLMServiceError as exc:
```
Catches controlled structured service failures.

```python
raise HTTPException(status_code=503, detail={...}) from exc
```
Returns a predictable HTTP error response when the LLM or parsing flow fails.

### Design Decision
The route handles HTTP concerns only:
- URL
- request model
- response model
- HTTP error status

Prompting, LLM calls, and parsing stay outside the route.

### Interview Explanation
I added `/chat/structured` as a separate endpoint instead of changing `/chat`. This preserves the V1 behavior while exposing the new V2 structured-output workflow. The route reuses `ChatRequest`, returns `StructuredLLMResponse`, and converts service failures into a controlled `503`.

## 7. `tests/unit/test_structured_schemas.py`

### Purpose
Tests the structured response contract.

### What It Tests
- Valid structured data is accepted.
- Invalid `confidence` values are rejected.
- Invalid `status` values are rejected.
- Blank text fields are rejected.

### Key Idea
```python
with pytest.raises(ValidationError):
```
This means the test passes only if invalid data raises a validation error.

### Interview Explanation
I tested the schema directly so the contract is protected before any route or service logic runs. This proves invalid model output cannot silently enter the API response.

## 8. `tests/unit/test_structured_prompt.py`

### Purpose
Tests the structured prompt builder.

### What It Tests
- The final prompt includes the user's message.
- The prompt includes the prompt version.
- The prompt asks for valid JSON only.
- The prompt prevents markdown and hidden chain-of-thought.

### Key Idea
These tests protect important prompt requirements from accidental edits.

### Interview Explanation
I tested the prompt because prompt wording is part of the product behavior. If someone removes the JSON-only rule later, the tests should catch that.

## 9. `tests/unit/test_structured_parser.py`

### Purpose
Tests the parser in isolation.

### What It Tests
- Valid JSON becomes a `StructuredLLMResponse`.
- Invalid JSON raises `StructuredOutputParseError`.
- Valid JSON with invalid schema fields also raises `StructuredOutputParseError`.

### Key Idea
This test separates parser correctness from the actual LLM provider.

### Interview Explanation
The parser tests prove that raw model output is not trusted. The backend accepts only JSON that passes both syntax validation and schema validation.

## 10. `tests/unit/test_structured_llm_service.py`

### Purpose
Tests the structured service flow without making a real LLM call.

### What It Tests
- Successful raw JSON output becomes a typed structured response.
- LLM provider errors become `StructuredLLMServiceError`.
- Parser errors trigger one retry.
- Repeated parser errors return a fallback structured response.

### Important Mocking Detail
```python
patch("app.services.structured_llm_service.generate_answer", ...)
```
We patch `generate_answer` where it is used, not where it was originally defined.

### Interview Explanation
I mocked the LLM call so the test verifies service behavior without network calls, provider availability, or API cost. This keeps tests deterministic and lets us simulate retry/fallback behavior precisely.

## 11. `tests/integration/test_chat_endpoint.py`

### Purpose
Tests the API route layer.

### V2 Tests
- `/chat/structured` returns structured JSON on success.
- `/chat/structured` returns a controlled `503` when the structured service fails.
- `/chat/structured` can return a valid fallback response when the service returns one.

### Key Idea
The integration tests prove that routing, request validation, service delegation, response serialization, and error formatting work together.

### Interview Explanation
The unit tests prove each piece works alone. The integration tests prove the FastAPI endpoint connects those pieces correctly.

## 12. End-to-End Manual Check

### Command
```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat/structured" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Explain missing values in a dataset in simple words."}'
```

### Expected Fields
```text
answer
confidence
reasoning_summary
next_action
prompt_version
status
```

### Why This Matters
Mocked tests prove code behavior under controlled conditions. The manual check proves the real provider path works end to end.

## 13. V2 Final Mental Model

```text
schemas/
  define what valid structured output means

prompts/
  instruct the LLM to return that output

services/structured_parser.py
  validates raw LLM output

services/structured_llm_service.py
  coordinates prompt, LLM call, and parsing

api/routes_chat.py
  exposes the feature through HTTP

tests/unit/
  test individual pieces

tests/integration/
  test pieces working together through FastAPI
```

## 14. V2 Codebase Interview Summary
In V2, I added a structured-output workflow to the existing FastAPI LLM backend. I created a strict Pydantic schema for model responses, a versioned prompt that asks for JSON only, a parser that validates raw LLM output, and a service layer that coordinates the prompt, provider call, parser, retry, and fallback behavior. Then I exposed the workflow through `POST /chat/structured`. I tested each layer with unit tests and tested the endpoint with integration tests. This makes the backend more reliable because future features can depend on a predictable response contract instead of free-form LLM text.
