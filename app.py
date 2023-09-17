from langchain.llms import LlamaCpp
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.llms import OpenAI

from dotenv import load_dotenv
import re

load_dotenv()

from flask import Flask, render_template, request

from utils import add_waypoints, avoid_area, prefer_path_type


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
    max_tokens=20,
    n_ctx=2048,
    top_p=1,
    f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
    verbose=True, # Verbose is required to pass to the callback manager
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def plan():
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
    result = chain.run(request.form['content'])
    print(result)

    pattern = ".*Assistant:.*\)"
    match = re.search(pattern, result)[0]

    content = match.split("Assistant:")[-1]
    function = content.split("(")[0]
    parameter = " ".join(content.split("(")[-1].split(")")[0].split("_")).strip("\"\',.`")

    return render_template('render.html', function=function, input_text=parameter)  