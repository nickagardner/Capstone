from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

import re

def choose_func(text, llm):
    template = """You are a helpful assistant who parses text and determines what change the user is requesting. 
    A user will pass in text, which you should parse to determine which change is requested. Return ONLY a function call and nothing more. 

    Change options are as follows:
        1. avoid_area - add if the user requests to avoid a particular area, or to not take a particular route.
        2. add_waypoints - add if the user requests to add additional stops to their route, or if they want to route through a destination.
        3. prefer_path_type - add if the user specifies a type of path that is preferred. Options include trails, gravel,
        bike lanes, paved, dirt, street. 
    
    For instance, if the user inputs: `prefer trails`, you should output: prefer_path_type(`trails`). 
    If the user inputs: `route through boston common`, you should output: add_waypoints(`boston common`)."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
    )
    result = chain.run(text)

    pattern = ".*Assistant:.*\)"
    match = re.search(pattern, result)[0]

    content = match.split("Assistant:")[-1]
    function = content.split("(")[0]
    parameter = " ".join(content.split("(")[-1].split(")")[0].split("_")).strip("\"\',.`")

    return function, parameter
