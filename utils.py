import json
import os

def avoid_area(obstacle, change_dict):
    """Run with anything that the user asks to avoid."""
    change_dict["avoid"].append(obstacle)
    print(f"Avoid added: {obstacle}")


def add_waypoints(waypoint, change_dict):
    """Run if the user wants to route through additional locations."""
    dict_item = {"location": waypoint, "stopover": True}
    change_dict["waypoints"].append(dict_item)
    print(f"Waypoint added: {waypoint}")


def prefer_path_type(type, change_dict):
    """Run if the user specifies a particular path type they would prefer."""
    change_dict["path_type"].append(type)
    print(f"Path type added: {type}")

def get_changes_dict():
    with open(os.path.join(os.path.abspath(os.curdir), "project", "static/js/changes.json"), "r") as file:
        change_dict = json.load(file)
    return change_dict

def update_changes_file(change_dict):
    with open(os.path.join(os.path.abspath(os.curdir), "project", "static/js/changes.json"), "w") as file:
        json.dump(change_dict, file)

def init_changes_file():
    change_dict = {"waypoints": [], "avoid": [], "path_type": ""}
    update_changes_file(change_dict)