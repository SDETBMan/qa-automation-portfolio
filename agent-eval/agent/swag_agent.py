"""
swag_agent.py — OpenAI function-calling agent for Swag Labs customer support.

SwagAgent is the system under test for agent-eval. It differs from both
ai-eval's answer_generator (stateless RAG) and conv-eval's SwagSupportBot
(stateful chat) in a key architectural way:

  SwagAgent uses OpenAI function calling to decide WHICH tools to invoke
  and with WHAT arguments, executes those tools, observes the results, and
  synthesizes a grounded final response — all in a multi-step loop.

This is what "agentic" means in practice: the model orchestrates tool use
rather than just generating text. The evaluation questions shift accordingly:
  - Did it call the right tool(s)?          → ToolCorrectnessMetric
  - Did it complete the user's task?        → TaskCompletionMetric

call_stats accumulates per-API-call latency and token usage across every step
in the agent loop (tool-selection calls + final synthesis call). The conftest
bot fixture teardown emits these to DataDog after each test.
"""

import json
import time as _time

from openai import OpenAI
from deepeval.test_case import ToolCall

from agent.tools import TOOL_DEFINITIONS, execute_tool

SYSTEM_PROMPT = (
    "You are a helpful Swag Labs customer support agent. "
    "You have access to tools to look up product details, check return eligibility, "
    "calculate shipping costs, and retrieve account status. "
    "Always use the available tools to answer questions accurately — "
    "do not answer from memory alone. "
    "When you have all the information you need, respond clearly and concisely."
)

_MAX_ITERATIONS = 6  # guard against runaway tool-call loops


class SwagAgent:
    """
    Stateless function-calling agent — each call to run() starts a fresh
    message thread and returns the final response plus a record of every
    tool that was called (in DeepEval ToolCall format for evaluation).
    """

    def __init__(self, client: OpenAI) -> None:
        self._client = client
        self._call_stats: list[dict] = []

    def run(self, query: str) -> tuple[str, list[ToolCall]]:
        """
        Execute the agent loop for a single user query.

        Returns:
            (final_response, tools_called) where tools_called is a list of
            DeepEval ToolCall objects recording what was invoked, with what
            arguments, and what each tool returned.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ]
        tools_called: list[ToolCall] = []

        for _ in range(_MAX_ITERATIONS):
            t0 = _time.time()
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            latency_ms = (_time.time() - t0) * 1000

            stat: dict = {"latency_ms": latency_ms}
            if response.usage:
                stat["prompt_tokens"]     = response.usage.prompt_tokens
                stat["completion_tokens"] = response.usage.completion_tokens
                stat["total_tokens"]      = response.usage.total_tokens
            self._call_stats.append(stat)

            message = response.choices[0].message

            # No tool calls → the agent has a final answer
            if not message.tool_calls:
                return message.content, tools_called

            # Append assistant message (with tool_calls) to history
            messages.append(message)

            # Execute each requested tool and feed results back
            for openai_tc in message.tool_calls:
                name   = openai_tc.function.name
                args   = json.loads(openai_tc.function.arguments)
                result = execute_tool(name, args)

                # Record in DeepEval format for ToolCorrectnessMetric
                tools_called.append(
                    ToolCall(
                        name=name,
                        input_parameters=args,
                        output=json.dumps(result),
                    )
                )

                # Feed tool result back into the conversation
                messages.append({
                    "role":         "tool",
                    "tool_call_id": openai_tc.id,
                    "content":      json.dumps(result),
                })

        # Fallback: max iterations reached without a final text response
        return "I was unable to complete your request within the allowed steps.", tools_called

    @property
    def call_stats(self) -> list[dict]:
        """Accumulated per-call stats for all API calls made during this instance's lifetime."""
        return self._call_stats
