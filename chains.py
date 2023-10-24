from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import BaseOutputParser
from langchain.chains import LLMChain

import re

class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""


    def parse(self, text: str):
        """Parse the output of an LLM call."""
        return text.strip().split(", ")

def choose_func(text, llm):
    template = """You are a helpful assistant who parses text and determines what change the user is requesting. 
    A user will pass in text, which you should parse to determine which change is requested. 
    Return ONLY the response to the last user request and nothing more.

    Change options are as follows:
        1. avoid_area - add if the user requests to avoid a particular area, or to not take a particular route.
        2. add_waypoints - add if the user requests to add additional stops to their route, or if they want to route through a destination.
        3. prefer_path_type - add if the user specifies a type of path surface that is preferred.
    
    User: prefer trails
    Assistant: prefer_path_type | trails

    User: stop at boston common
    Assistant: add_waypoints | boston common

    User: avoid main street
    Assistant: avoid_area | main street

    User: route through north ave and Susan B. Anthony Museum & House
    Assistant: add_waypoints | north ave | Susan B. Anthony Museum & House

    User: avoid johnson bridge and 17 Madison St
    Assistant: avoid_area | johnson bridge | 17 Madison St

    User: I want to ride on roads
    Asssistant: prefer_path_type | roads
    
    User: """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
    )

    result = chain.run(text)
    print(result)
    result = result + "\n"

    pattern = ".*Assistant:.*\n"
    match = re.search(pattern, result)[0]

    content = match.split("Assistant:")[-1]
    components = content.split("|")
    function = components[0].strip()
    parameters = []
    for parameter in components[1:]:
        parameters.append(parameter.strip("\"\',.`\n "))

    return function, parameters

def split_changes(text, llm):
    template = """You are a helpful assistant who parses text and splits the text into discrete requests.
    Return ONLY the response to the last user response and nothing more.
    
    User: I want to ride on trails and avoid main street
    Assistant: I want to ride on trails | avoid main street

    User: stop at boston common and the empire state building
    Assistant: stop at boston common and the empire state building

    User: avoid 42nd ave
    Assistant: avoid 42nd ave

    User: prefer roads. route through north ave and Susan B. Anthony Museum & House
    Assistant: prefer roads | route through north ave and Susan B. Anthony Museum & House

    User: avoid johnson bridge and 17 Madison St
    Assistant: avoid johnson bridge and 17 Madison St

    User: pass through the airport. use city streets
    Asssistant: pass through the airport | use city streets
    
    User: """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
        output_parser=CommaSeparatedListOutputParser()
    )
    result = chain.run(text)[0]
    result = result + "\n"

    print(result)

    pattern = ".*Assistant:.*\n"
    match = re.search(pattern, result)[0]

    content = match.split("Assistant:")[-1]
    components = content.split("|")
    requests = []
    for parameter in components:
        requests.append(parameter.strip("\"\',.`\n "))

    return requests
