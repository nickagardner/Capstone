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

    User: route through north cemetery and Susan B. Anthony Museum & House
    Assistant: add_waypoints | north cemetery | Susan B. Anthony Museum & House

    User: avoid johnson bridge and 17 Madison St
    Assistant: avoid_area | johnson bridge | 17 Madison St

    User: want to ride on gravel and bike lanes only
    Asssistant: prefer_path_type | gravel | bike lanes
    
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

    pattern = ".*Assistant:.*\n"
    match = re.search(pattern, result)[0]

    content = match.split("Assistant:")[-1]
    components = content.split("|")
    function = components[0].strip()
    parameters = []
    for parameter in components[1:]:
        parameters.append(parameter.strip("\"\',.`\n"))

    return function, parameters

def split_changes(text, llm):
    # template = """You are a helpful assistant who parses text and splits it into discrete requests. 
    # A user will pass in one or more sentences containing change requests, which you should split into each 
    # requested change and return as a comma separated list. Return ONLY a comma separated list and nothing more. 
    # Do not add any characters that the user did not include in their request. 
    
    # For instance, if the user inputs: `prefer trails. avoid central park`, you should output: [`prefer trails`, `avoid central park`]. 
    # If the user inputs: `avoid main street and prefer gravel paths`, you should output: [`avoid main street`, `prefer gravel paths`]"""

    # system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    # human_template = "{text}"
    # human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    # chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    # chain = LLMChain(
    #     llm=llm,
    #     prompt=chat_prompt,
    #     output_parser=CommaSeparatedListOutputParser()
    # )
    # result = chain.run(text)

    # pattern = ".*Assistant:.*\)"
    # match = re.search(pattern, result)[0]

    # content = match.split("Assistant:")[-1]
    # function = content.split("(")[0]
    # parameter = " ".join(content.split("(")[-1].split(")")[0].split("_")).strip("\"\',.`")

    result = text.split(".")

    return result
