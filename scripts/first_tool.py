import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# The actual Python functions
def get_current_time() -> str:
    """Returns the current time as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_numbers(a: float, b: float) -> float:
    """Adds two numbers and returns the sum."""
    return a + b


# Map tool names to the actual functions so we can dispatch by name
TOOL_REGISTRY = {
    "get_current_time": get_current_time,
    "add_numbers": add_numbers,
}


# Tell the model what tools exist and how to call them
tools = [
    types.Tool(function_declarations=[
        {
            "name": "get_current_time",
            "description": "Returns the current date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "add_numbers",
            "description": "Adds two numbers together and returns the sum.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    ])
]

config = types.GenerateContentConfig(tools=tools)


def run_agent(user_question: str, max_iterations: int = 5) -> str:
    """Run a simple agent loop until the model stops calling tools."""
    contents = [types.Content(role="user", parts=[types.Part(text=user_question)])]

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=config,
        )

        # Grab the model's response and add it to history
        # print(response)
        candidate = response.candidates[0]
        contents.append(candidate.content)

        # Look for function calls in the response
        
        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if part.function_call
        ]
        # print(function_calls)

        if not function_calls:
            # No more tool calls, model is done
            print("Model finished, returning final answer.")
            return response.text

        # Execute each requested tool call
        function_response_parts = []
        for fc in function_calls:
            tool_name = fc.name
            
            tool_args = dict(fc.args) if fc.args else {}
            # print(type(tool_args))
            print(f"Model wants to call: {tool_name}({tool_args})")

            if tool_name not in TOOL_REGISTRY:
                result = {"error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    result = {"result": TOOL_REGISTRY[tool_name](**tool_args)}
                except Exception as e:
                    result = {"error": str(e)}

            print(f"Tool returned: {result}")

            function_response_parts.append(
                types.Part.from_function_response(name=tool_name, response=result)
            )

        # Feed the tool results back to the model
        contents.append(types.Content(role="user", parts=function_response_parts))
        print(contents)
        

    return "Max iterations reached without a final answer."


if __name__ == "__main__":
    question = "what's the time also sum 1233 + -2323"
    answer = run_agent(question)
    print(f"\n=== FINAL ANSWER ===\n{answer}")