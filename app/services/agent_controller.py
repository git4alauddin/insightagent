from app.prompts.tool_router_v3 import build_tool_router_prompt
from app.schemas.agent import AgentQueryResponse, ToolDecision
from app.services.llm_service import LLMServiceError, generate_answer
from app.services.tool_decision_parser import ToolDecisionParseError, parse_tool_decision
from app.tools.registry import ToolRegistryError, get_tool, initialize_tool_registry


class AgentControllerError(Exception):
    pass


def _build_none_tool_response(user_message: str, reason: str) -> AgentQueryResponse:
    return AgentQueryResponse(
        answer=f"No tool was required for this request: {user_message}",
        confidence="medium",
        tool_used="none",
        tool_input={},
        tool_output_summary=reason,
        tool_status="skipped",
        status="success",
    )


def _execute_tool(decision: ToolDecision) -> str:
    try:
        tool_fn = get_tool(decision.tool_name)
    except ToolRegistryError as exc:
        raise AgentControllerError(str(exc)) from exc

    try:
        return tool_fn(decision.tool_input)
    except Exception as exc:
        raise AgentControllerError(f"Tool execution failed: {decision.tool_name}") from exc


def run_agent_query(message: str) -> AgentQueryResponse:
    initialize_tool_registry()
    prompt = build_tool_router_prompt(message)

    try:
        raw_decision_output = generate_answer(prompt)
    except LLMServiceError as exc:
        raise AgentControllerError(str(exc)) from exc

    try:
        decision = parse_tool_decision(raw_decision_output)
    except ToolDecisionParseError as exc:
        raise AgentControllerError(str(exc)) from exc

    if decision.tool_name == "none":
        return _build_none_tool_response(message, decision.reason)

    tool_output = _execute_tool(decision)

    return AgentQueryResponse(
        answer=f"Tool '{decision.tool_name}' completed successfully.",
        confidence="high",
        tool_used=decision.tool_name,
        tool_input=decision.tool_input,
        tool_output_summary=tool_output,
        tool_status="success",
        status="success",
    )

