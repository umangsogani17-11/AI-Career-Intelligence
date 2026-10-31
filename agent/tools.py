def calculator(operation, num1, num2):
    """
    Performs basic mathematical calculations.
    """

    if operation == "add":
        return num1 + num2

    elif operation == "subtract":
        return num1 - num2

    elif operation == "multiply":
        return num1 * num2

    elif operation == "divide":
        if num2 == 0:
            return "Error: Cannot divide by zero"
        return num1 / num2

    else:
        return "Invalid operation"


def calculate_from_expression(expression):
    """
    Simple calculator for expressions like:
    10 + 20
    50 - 10
    5 * 6
    20 / 4
    """

    parts = expression.split()

    if len(parts) != 3:
        return "Invalid expression. Use: number operator number"

    num1 = float(parts[0])
    operator = parts[1]
    num2 = float(parts[2])

    if operator == "+":
        return calculator("add", num1, num2)

    elif operator == "-":
        return calculator("subtract", num1, num2)

    elif operator == "*":
        return calculator("multiply", num1, num2)

    elif operator == "/":
        return calculator("divide", num1, num2)

    else:
        return "Unknown operator"