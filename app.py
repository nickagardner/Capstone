from langchain.llms import LlamaCpp
from langchain.llms import OpenAI

from dotenv import load_dotenv
import os
load_dotenv()

from flask import Flask, render_template, request, jsonify

from utils import add_waypoints, avoid_area, prefer_path_type
from chains import choose_func, split_changes


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

@app.route('/', methods=["POST","GET"])
def index():
    if request.method == "POST":
        todo = request.form.get("todo")
        print(todo)
    return render_template('index.html', 
                           google_maps_string=f"https://maps.googleapis.com/maps/api/js?key={os.environ['GOOGLE_MAPS_API_KEY']}&libraries=places&callback=initMap")

# @app.route('/', methods=['POST'])
# def plan():
#     changes = split_changes(request.form['content'], llm)
#     functions = []
#     parameters = []
#     for change in changes:
#         if len(change) > 0:
#             function, parameter = choose_func(change, llm)
#             functions.append(function)
#             parameters.append(parameter)
#             possibles = globals().copy()
#             possibles.update(locals())
#             method = possibles.get(function)
#             if not method:
#                 raise NotImplementedError("Method %s not implemented" % function)
#             print(method(parameter))

    # return render_template('render.html', function=functions, input_text=parameters) # requests=requests) 