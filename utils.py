import json
import os

def avoid_area(obstacle, output_dict):
    """Run with anything that the user asks to avoid."""
    return f"Need to avoid: {obstacle}"


def add_waypoints(waypoint, session):
    """Run if the user wants to route through additional locations."""
    dict_item = {"location": waypoint, "stopover": False}
    session["output_dict"]["waypoints"].append(dict_item)
    print(f"Waypoint added: {waypoint}")


def prefer_path_type(type, output_dict):
    """Run if the user specifies a particular path type they would prefer."""
    return f"Preferred path type: {type}"

def update_changes_file(session):
    with open(os.path.join(os.path.abspath(os.curdir), "project", "static/js/changes.json"), "w") as file:
        json.dump(session.get('output_dict', None), file)

def init_changes_file(session):
    session["output_dict"] = {"waypoints": [], "avoid": [], "path_type": ""}
    update_changes_file(session)