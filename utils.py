import json
import os

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
    if "trails" in type:
        change_dict["path_type"] = "mountain_bike"
    elif "roads" in type:
        change_dict["path_type"] = "road_bike"
    elif "city" in type:
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
                   "avoided_already":[], "avoided_locs":[], "api_key": os.environ["GEOAPIFY_KEY"]}
    update_changes_file(change_dict)