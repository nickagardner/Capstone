from langchain.tools import tool

@tool
def avoid_area(obstacle):
    """Run with anything that the user asks to avoid."""
    return f"Need to avoid: {obstacle}"
@tool
def add_waypoints(waypoint):
    """Run if the user wants to route through additional locations."""
    return f"Waypoint added: {waypoint}"
@tool
def prefer_path_type(type):
    """Run if the user specifies a particular path type they would prefer."""
    return f"Preferred path type: {type}"