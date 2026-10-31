import json

from agent.router import decide_tool
from agent.tools import calculate_from_expression


def execute_request(user_request):

    # Step 1: Ask Nemotron which tool to use
    decision = decide_tool(user_request)

    print("\nAI Decision:")
    print(decision)

    # Step 2: Convert AI response into Python dictionary
    try:
        decision_data = json.loads(decision)
    except json.JSONDecodeError:
        return "AI returned an invalid decision."

    tool = decision_data.get("tool")

    # Step 3: Execute calculator
    if tool == "calculator":

        result = calculate_from_expression(user_request)

        return f"Calculator Result: {result}"

    # Step 4: File manager will be connected next
    elif tool == "file_manager":

        return "File Manager selected. We will connect it in the next step."

    # Step 5: Normal AI response
    elif tool == "none":

        return "No tool required."

    else:

        return "Unknown tool selected."


if __name__ == "__main__":

    print("==============================")
    print("   AI CAREER INTELLIGENCE")
    print("==============================")

    request = input("\nEnter your request: ")

    result = execute_request(request)

    print("\nFinal Result:")
    print(result)