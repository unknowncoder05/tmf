from gpt import GPTPetition
from datetime import datetime
import re
import json
import openai
import os


def default_function(*args, **kwargs):
    print("FUNCTION CALL:", args, kwargs)


openai.api_key = os.getenv("OPEN_AI_API_KEY")
MODEL = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo", "gpt-4", "gpt-4-0613"][2]
CONTEXT = """
s: use this data and call the save function
u: Python advanced, Javascript, AWS, Pytest, Mocha
"""
FUNCTIONS = [
    {
        "function": default_function,
        "name": "save_skills",
        "description": "saves the skills of an user",
        "parameters": {
            "skills": {
                "type": "array",
                "description": "list of skills",
                "items": {
                    "type": "object",
                    "properties": {
                        "rating": {
                            "type": "integer",
                            "description": "Rating from 1 to 5, default to 1 if ",
                        },
                        "skill": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the skill",
                                }
                            },
                        },
                    },
                },
            }
        },
    }
]


def transform_string_to_messages(string):
    messages = []
    current_message = None

    lines = string.strip().split("\n")
    for line in lines:
        line = line.strip()

        if re.match(r"^[sau]:", line):
            # Start of a new message
            if current_message is not None:
                messages.append(current_message)

            role, content = line.split(":", 1)
            if role == "a":
                role = "assistant"
            elif role == "s":
                role = "system"
            elif role == "u":
                role = "user"
            current_message = {"role": role, "content": [content.strip()]}
        elif current_message is not None:
            # Append content to the current message
            current_message["content"].append(line.strip())

    # Append the last message
    if current_message is not None:
        messages.append(current_message)

    return messages


messages = transform_string_to_messages(CONTEXT)
petition = GPTPetition(MODEL)

for message in messages:
    role = message["role"]
    message = "/n".join(message["content"])
    petition._add_message(role, message)


def default_function(*args, **kwargs):
    print(args, kwargs)


for function in FUNCTIONS:
    petition.add_function(**function)

response = petition.execute(function_call={"name": "save_skills"})
verbose_response = response["role"] + ": " + response["content"]
with open(f"samples/{datetime.now().ctime()}", "w") as f:
    f.write("MODEL\n" + MODEL)
    f.write("\nCONTEXT\n" + CONTEXT)
    verbose_functions = json.dumps(
        [
            {key: function[key] for key in function if key != "function"}
            for function in FUNCTIONS
        ]
    )
    f.write("\nFUNCTIONS\n" + verbose_functions)
    f.write("\nRESPONSE\n" + verbose_response)
