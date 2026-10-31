import os
from dotenv import load_dotenv
from openai import OpenAI

try:
    from .file_manager import list_project_files, read_project_file, create_project_file
except ImportError:  # Supports running this file directly as well as as a module.
    from file_manager import list_project_files, read_project_file, create_project_file

# Load environment variables
load_dotenv()


# Create NVIDIA client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)


MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"


def get_project_context():
    """
    Read important project files and prepare
    their contents for Nemotron.
    """

    files = list_project_files()

    context = ""

    for file in files:

        # Don't send secret/API files to AI
        if file in [".env"]:
            continue

        try:
            content = read_project_file(file)

            context += f"""
========== FILE: {file} ==========

{content}

"""

        except Exception as error:
            print(f"Could not read {file}: {error}")

    return context


def ask_nemotron(question):

    project_context = get_project_context()

    prompt = f"""
You are an AI coding assistant.

You are analyzing a software project called:

AI Career Intelligence

Here are the current project files:

{project_context}

User's question:

{question}

Instructions:

1. Understand the existing project before answering.
2. Do not invent files that do not exist.
3. Clearly explain what you found.
4. If something is missing, say that it is missing.
5. Do not modify any files.
6. Give beginner-friendly explanations.
"""


    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a senior software engineer helping a student."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1500
    )

    return response.choices[0].message.content


def create_file_with_ai():

    print("\nWhat file do you want to create?")

    request = input("> ")

    prompt = f"""
You are a coding assistant.

The user wants:

{request}

Generate the complete content for the requested file.

Return your answer in EXACTLY this format:

FILE_NAME: filename.py

FILE_CONTENT:
<complete code here>

Do not add explanations.
Do not use markdown code fences.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert Python developer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=2000
    )

    ai_response = response.choices[0].message.content

    print("\n========== AI RESPONSE ==========\n")
    print(ai_response)

    # Extract filename
    if "FILE_NAME:" not in ai_response:
        print("\nCould not understand AI response.")
        return

    filename_part = ai_response.split("FILE_NAME:", 1)[1]

    filename = filename_part.split("\n", 1)[0].strip()

    # Extract content
    if "FILE_CONTENT:" not in ai_response:
        print("\nFile content was not generated.")
        return

    content = ai_response.split(
        "FILE_CONTENT:",
        1
    )[1].strip()

    # Create the file
    try:

        result = create_project_file(
            filename,
            content
        )

        print("\n" + result)

    except Exception as error:

        print(
            f"\nFile creation failed: {error}"
        )


if __name__ == "__main__":

    print("\n================================")
    print("   AI CAREER INTELLIGENCE AGENT")
    print("================================")

    print("\n1. Analyze project")
    print("2. Create a file")

    choice = input("\nChoose an option: ")

    if choice == "1":

        question = input(
            "\nWhat do you want Nemotron to analyze? "
        )

        print("\nThinking...\n")

        answer = ask_nemotron(question)

        print(
            "\n========== NEMOTRON ==========\n"
        )

        print(answer)

    elif choice == "2":

        create_file_with_ai()

    else:

        print("\nInvalid choice.")
