import openai
import json
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ModelResponseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class GPTPetition:
    functions: dict = {}

    def __init__(self, model_name='gpt-3.5-turbo-0613'):
        self.model_name = model_name
        self.messages = list()
        return

    def add_function(self, function, name, description, parameters):
        self.functions[name] = dict(
            definition=dict(
                name=name,
                description=description,
                parameters={
                    "type": "object",
                    "properties": parameters,
                    "required": ["role"],
                }
            ),
            function=function
        )
        logger.debug(f"GPT: Added function {name}")

    def _add_message(self, role, content):
        self.messages.append(dict(role=role, content=content))

    def system(self, content):
        self._add_message('system', content)
    
    def user(self, content):
        self._add_message('user', content)
    
    def assistant(self, content):
        self._add_message('assistant', content)

    def execute(self, temperature=0, calls=0, function_call="auto", **kwargs):
        logger.debug(f"GPT: api call {self.messages}")
        print("MESSAGES")
        for message in self.messages:
            print(message['role'], ":", message['content'])
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.messages,
            functions=[f['definition'] for f in self.functions.values()],
            function_call=function_call,
            temperature=temperature,
            **kwargs
        )

        message = response["choices"][0]["message"]
        print("R :", message)

        # Step 2, check if the model wants to call a function
        if message.get("function_call"):
            logger.debug(f"GPT: function_call {message}")
            function_name = message["function_call"]["name"]

            # Args
            try:
                function_args = json.loads(
                    message["function_call"]["arguments"])
            except json.decoder.JSONDecodeError:
                raise ModelResponseError(
                    'model response arguments not in json')

            if function_name not in self.functions:
                raise ModelResponseError(
                    f'"{function_name}" function not registered')

            function = self.functions[function_name]['function']

            # Function call
            try:
                function_response = function(**function_args)
                function_response = json.dumps(function_response)
            except TypeError as e:
                logger.error(f"GPT: {e}")
                raise ModelResponseError('model response arguments invalid')

            self.messages.extend([
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            ])

            # Step 4, send model the info on the function call and function response
            second_response = self.execute(temperature, calls+1)
            return second_response
        return message


if __name__ == '__main__':
    import os
    import openai
    openai.api_key = os.getenv("OPEN_AI_API_KEY")
    from api.jobai.services.gpt import GPTPetition

    petition = GPTPetition()
    petition.system("""you are a job seeking assistant that:
    1. gets the missing user information and saves it, you want to follow this route
        a. collect name "To start, could you pleas tell me your full name?"
        b. collect contact info "Could you please provide your phone number, email address ..."
        c. collect objective/summary "Do you have a short professional summary or career objective you'd like to add at the top of your resume? if you are unsure, I can help guide you"
    2. if the user asks you to make an action that is not in this list, say "am sorry but that is out of my current capabilities"
    """)
    petition.user('take me to the moon')

    def get_jobs_by_rol(role):
        return ['gugle','facebuk']

    petition.add_function(
        get_jobs_by_rol,
        'get_jobs_by_rol',
        'gets the best job matches for an specific role',
        {
            "role": {
                "type": "string",
                "description": "name of the professional role",
            }
        },
    )

    print(petition.execute())
