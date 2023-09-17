from langchain.llms import LlamaCpp
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.agents.tools import Tool
from langchain import LLMMathChain

from langchain.chat_models import ChatOpenAI
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain.llms import OpenAI
from langchain import SerpAPIWrapper
from langchain.agents.tools import Tool
from langchain import LLMMathChain

from dotenv import load_dotenv

load_dotenv()


def plan():
    llm = OpenAI(temperature=0)
    llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=False)
    # model = LlamaCpp(
    # model_path="/Users/ng/Documents/2023 Fall/Capstone/llama.cpp/models/7B/gguf-llama2-q4_0.bin",
    # temperature=0,
    # verbose=True, # Verbose is required to pass to the callback manager
    # )
    model = ChatOpenAI(temperature=0)
    tools = [
        Tool(
            name="Calculator",
            func=llm_math_chain.run,
            description="useful for when you need to answer questions about math"
        ),
    ]
    planner = load_chat_planner(model)
    executor = load_agent_executor(model, tools, verbose=True)
    agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
    return agent.run("What is 25 raised to the 2 power?")

plan()