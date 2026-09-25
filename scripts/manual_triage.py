"""Manually trigger the agent on one issue to verify tools wire up correctly."""
import json
import os
from dotenv import load_dotenv
from groq import Groq
from src.tool_schemas import TOOLS, TOOL_REGISTRY

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-20b"

SYSTEM_INSTRUCTION = """You are a GitHub issue triage assistant. Given an issue, you should:
1. Read the issue to understand it.
2. Check what labels exist in the repo.
3. Add appropriate labels (bug, enhancement, question, documentation, etc.).
4. Post a short comment acknowledging the issue and, if needed, ask for missing info.

Be concise and helpful. You MUST call list_available_labels before add_labels_to_issue.
Only use labels that already exist in the repo."""


def run(user_request: str, max_iterations: int = 10) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_request},
    ]

    for i in range(max_iterations):
        print(f"\n--- Iteration {i + 1} ---")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            print("Agent done.")
            return msg.content or "(no text response)"

        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"→ {name}({args})")

            fn = TOOL_REGISTRY.get(name)
            if fn is None:
                result = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = {"error": str(e)}
            print(f"  ← {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

    return "Max iterations reached."


if __name__ == "__main__":
    sandbox = os.getenv("SANDBOX_REPO")
    request = f"Please triage issue #3 in the repo {sandbox}."
    result = run(request)
    print(f"\n=== FINAL ===\n{result}")