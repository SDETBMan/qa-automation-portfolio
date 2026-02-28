"""
swag_support_bot.py — Stateful Swag Labs customer support chatbot.

SwagSupportBot wraps an OpenAI chat completions call and maintains a running
message history, making it the stateful "system under test" for conv-eval.

This is the key architectural difference from ai-eval's answer_generator:
  - answer_generator (ai-eval): stateless — takes question + context, returns answer.
  - SwagSupportBot (conv-eval): stateful — accumulates the full conversation history
    across turns so the model can resolve pronouns, follow topic switches, and
    acknowledge corrections, exactly like a real support chatbot would.

CHATBOT_ROLE is exported for use in DeepEval's RoleAdherenceMetric and
ConversationalTestCase — it defines the persona the metric will evaluate against.
"""

import time as _time

from openai import OpenAI

from chatbot.knowledge import SYSTEM_PROMPT

CHATBOT_ROLE = (
    "a friendly Swag Labs customer support agent who exclusively answers questions "
    "about Swag Labs products, pricing, checkout, shipping, returns, and account "
    "access, and politely declines all requests that fall outside that domain"
)


class SwagSupportBot:
    """
    Stateful chatbot for the Swag Labs support domain.

    Each instance holds its own message history, so every test that receives
    a fresh bot fixture starts from a clean slate. Call chat() sequentially
    to simulate a real multi-turn customer conversation.
    """

    def __init__(self, client: OpenAI) -> None:
        self._client = client
        self._messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self._call_stats: list[dict] = []

    def chat(self, user_message: str) -> str:
        """Send a user message and return the bot's response.

        Appends both the user message and the assistant reply to the internal
        history so subsequent turns have full conversational context.
        Records per-call latency and token usage in call_stats for the fixture
        teardown to emit to DataDog.
        """
        self._messages.append({"role": "user", "content": user_message})

        t0 = _time.time()
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=self._messages,
        )
        latency_ms = (_time.time() - t0) * 1000

        reply: str = response.choices[0].message.content
        self._messages.append({"role": "assistant", "content": reply})

        stat = {"latency_ms": latency_ms}
        if response.usage:
            stat["prompt_tokens"]     = response.usage.prompt_tokens
            stat["completion_tokens"] = response.usage.completion_tokens
            stat["total_tokens"]      = response.usage.total_tokens
        self._call_stats.append(stat)

        return reply

    @property
    def call_stats(self) -> list[dict]:
        """Per-call latency and token usage recorded during this session."""
        return self._call_stats

    @property
    def history(self) -> list[dict]:
        """Conversation history excluding the system prompt."""
        return [m for m in self._messages if m["role"] != "system"]
