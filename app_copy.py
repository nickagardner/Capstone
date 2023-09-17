from langchain.llms import LlamaCpp
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.agents.tools import Tool
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.llms import OpenAI

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template

from utils import add_waypoint, avoid_area, prefer_path_type


app = Flask(__name__)

# llm = OpenAI(temperature=0)

n_gpu_layers = 1  # Metal set to 1 is enough.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.
# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="/Users/ng/Documents/2023 Fall/Capstone/project/llama.cpp/models/13B-chat/gguf-llama2-q4_0.bin",
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    temperature=0,
    max_tokens=2000,
    n_ctx=2048,
    top_p=1,
    f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
    verbose=True, # Verbose is required to pass to the callback manager
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan')
def plan():
    # tools = [avoid_area, prefer_path_type, add_waypoint]

    template = """You are a helpful assistant who parses text and runs tools to complete the user's request. 
    A user will pass in text, which you should parse to determine which tools need to be run. Do not run any tools
    that the user does not ask for. Return any observations that you receive.
    
    For instance, if the user inputs: prefer trails. avoid W 42nd st, you should run Avoid Area with an input=W 42nd st
    and run Prefer Path Type with an input=trails. You should not run Add Waypoints, as the user did not request any stops
    added to their route."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    # chain = LLMChain(
    #     llm=ChatOpenAI(openai_api_key=req_info[0]),
    #     prompt=chat_prompt,
    #     output_parser=CommaSeparatedListOutputParser()
    # )
    
    # themes = chain.run(req_info[1:])
    tools = [
        Tool(
        name = "Avoid Area",
        func=avoid_area.run,
        description="""useful if the user requests to avoid an area. 
        The input to this tool should be a string representing the area the user requested to avoid.
        For example, `central park` would be the input if the user said to avoid central park."""
        ),
        Tool(
        name = "Prefer Path Type",
        func=prefer_path_type.run,
        description="""useful if the user requests a certain path type. 
        The input to this tool should be a string representing the path type the user prefers.
        For example, `gravel` would be the input if the user said they wanted a gravel path."""
        ),
        Tool(
        name = "Add Waypoints",
        func=add_waypoint.run,
        description="""useful if the user wants waypoints added to their route. 
        The input to this tool should be a comma separated list representing the waypoints the user wants to add.
        For example, `[boston common, boston city hall]` would be the input if the user said they wanted to route
        through the boston common and boston city hall."""
        ),
    ]
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, prompt=chat_prompt)
    return agent.run("prefer trails. avoid W 42nd st.")