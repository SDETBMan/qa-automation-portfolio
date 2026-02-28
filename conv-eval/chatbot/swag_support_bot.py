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

    def chat(self, user_message: str) -> str:
        """Send a user message and return the bot's response.

        Appends both the user message and the assistant reply to the internal
        history so subsequent turns have full conversational context.
        """
        self._messages.append({"role": "user", "content": user_message})

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=self._messages,
        )

        reply: str = response.choices[0].message.content
        self._messages.append({"role": "assistant", "content": reply})
        return reply

    @property
    def history(self) -> list[dict]:
        """Conversation history excluding the system prompt."""
        return [m for m in self._messages if m["role"] != "system"]
