import json
import os

from langchain.llms import LlamaCpp
from langchain.llms import OpenAI

from chains import choose_func, split_changes

conversion_dict = {"rd": "road", "st": "street", "dr": "drive", "ave": "avenue", "blvd": 
                   "boulevard", "ln": "lane", "pkwy": "parkway", "pl": "place", "ct": "court", 
                   "cir": "circle", "trl": "trail", "hwy": "highway", "sq": "square", "bl": "boulevard",
                   "ter": "terrace", "plz": "plaza", "n": "north", "s": "south", "e": "east", "w": "west",
                   "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest"}

def avoid_area(obstacle, change_dict):
    """Run with anything that the user asks to avoid."""
    change_dict["avoid"].append(obstacle)
    print(f"Avoid added: {obstacle}")


def add_waypoints(waypoint, change_dict):
    """Run if the user wants to route through additional locations."""
    change_dict["waypoints"].append(waypoint)
    print(f"Waypoint added: {waypoint}")


def prefer_path_type(type, change_dict):
    """Run if the user specifies a particular path type they would prefer."""
    type = type.lower()
    if "trails" in type or "trail" in type or "bike path" in type or "dirt" in type or "gravel" in type or "mountain" in type or "off-road" in type:
        change_dict["path_type"] = "mountain_bike"
    elif "roads" in type in type:
        change_dict["path_type"] = "road_bike"
    elif "city" in type or "bike lanes" in type:
        change_dict["path_type"] = "bicycle"
    print(f"Path type added: {type}")

def get_changes_dict():
    with open(os.path.join(os.path.abspath(os.curdir), "project", "static/js/changes.json"), "r") as file:
        change_dict = json.load(file)
    return change_dict

def update_changes_file(change_dict):
    with open(os.path.join(os.path.abspath(os.curdir), "project", "static/js/changes.json"), "w") as file:
        json.dump(change_dict, file)

def init_changes_file():
    change_dict = {"waypoints": [], "avoid": [], "path_type": "", "avoid_str": "", 
                   "avoided_already":[], "avoided_locs":[]}
    update_changes_file(change_dict)

def process_changes(todo, llm):
    change_dict = get_changes_dict()
    todo_sections = todo.split(".")
    for section in todo_sections:
        changes = split_changes(section, llm)
        functions = []
        parameters = []
        for change in changes:
            if len(change) > 0:
                function, new_parameters = choose_func(change, llm)
                for param in new_parameters:
                    functions.append(function)
                    parameters.append(param)
                    possibles = globals().copy()
                    possibles.update(locals())
                    method = possibles.get(function)
                    if not method:
                        raise NotImplementedError("Method %s not implemented" % function)
                    method(param, change_dict)
    update_changes_file(change_dict)

def instantiate_llm(open_ai=False):
    if open_ai:
        llm = OpenAI(temperature=0)
    else:
        n_gpu_layers = 1  # Metal set to 1 is enough.
        n_batch = 512  # Should be between 1 and n_ctx, consider the amount of RAM of your Apple Silicon Chip.
        # Make sure the model path is correct for your system!
        llm = LlamaCpp(
            model_path="/Users/ng/Documents/2023 Fall/Capstone/project/llama.cpp/models/13B-chat/gguf-llama2-q4_0.bin",
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            temperature=0,
            max_tokens=30,
            n_ctx=2048,
            top_p=1,
            f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
            verbose=True, # Verbose is required to pass to the callback manager
        )
    return llm

def process_string(check_string):
    name = check_string.lower()
    arr = name.split(" ")
    for i in range(len(arr)):
        if arr[i] in conversion_dict:
            arr[i] = conversion_dict[arr[i]]
    return " ".join(arr)