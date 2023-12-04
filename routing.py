import os
import requests

from utils import get_changes_dict, update_changes_file, process_string

def codeAddress(address, bounds):
    response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&bounds={bounds}&key={os.environ['GOOGLE_MAPS_API_KEY']}")

    if response.status_code == 200:
        json = response.json()
        if json["status"] == "ZERO_RESULTS":
            return None
        else:
            coords = response.json()["results"][0]["geometry"]["location"]
            return [coords["lat"], coords["lng"]]
    else:
        return None

def check_route(intermediate_result, avoid):
    avoid_name = process_string(avoid)
    coords = []
    for idx, leg in enumerate(intermediate_result["features"][0]["properties"]["legs"]):
        for step in leg["steps"]:
            try:
                name = process_string(step["name"])
                if avoid_name in name:
                    start_inds = step["from_index"]
                    coords.append(intermediate_result["features"][0]["geometry"]["coordinates"][idx][start_inds][::-1])
            except Exception as e:
                pass
    return coords

def distance(waypoint_coords, end_coords):
  return ((end_coords[0] - waypoint_coords[0])**2 + (end_coords[1] - waypoint_coords[1])**2)**0.5

def calc_route(start, end, bounds):
    change_dict = get_changes_dict()

    api_key = os.environ["GEOAPIFY_KEY"]
    avoid_str = change_dict["avoid_str"]
    avoided_already = change_dict["avoided_already"]
    avoided_locs = change_dict["avoided_locs"]
    
    start_coords = codeAddress(start, bounds)
    end_coords = codeAddress(end, bounds)

    bad_waypoint_inds = []
    bad_avoid_inds = []
    coord_array = []
    dist_array = []
    
    more_waypoints = ""

    path_type = "bicycle"

    if change_dict["waypoints"] != [] or change_dict["avoid"] != [] or change_dict["path_type"] != "":
        waypoints = change_dict["waypoints"]

        if len(waypoints) > 0:
            for idx, waypoint in enumerate(waypoints):
                coords = codeAddress(waypoint, bounds)
                if coords is not None: 
                    dist = distance(coords, end_coords)
                    if dist < 2: 
                        coord_array.append(coords)
                        dist_array.append(dist)
                    else:
                        bad_waypoint_inds.append(idx)
                        print("Waypoint too far from destination: " + waypoint)
                else:
                    bad_waypoint_inds.append(idx)
                    print("Unable to geocode waypoint: " + waypoint)

            sorted_array = [x for _, x in sorted(zip(dist_array, coord_array), reverse=True)]

            for coord in sorted_array:
                more_waypoints += ",".join(map(str, coord))
                more_waypoints += "|"

        path_type = change_dict["path_type"]
        if path_type == "":
            path_type = "bicycle"

        avoid = change_dict["avoid"]

        if len(avoid) > 0:
            url = f"https://api.geoapify.com/v1/routing?waypoints={','.join(map(str, start_coords))}|{more_waypoints}{','.join(map(str, end_coords))}&mode={path_type}&{avoid_str}details=route_details&apiKey={api_key}"
            intermediate_result = requests.get(url).json()

            for i in range(len(avoid)):
                if avoid[i] not in avoided_already:
                    coords = check_route(intermediate_result, avoid[i])
                    if len(coords) == 0:
                        new_coords = codeAddress(avoid[i], bounds)
                        if new_coords is not None:
                            dist = distance(new_coords, end_coords)
                            if dist < 1:
                                avoided_already.append(avoid[i])
                                avoided_locs.append(new_coords)
                            else:
                                bad_avoid_inds.append(i)
                                print("Avoid too far from route: " + avoid[i])
                        else:
                            bad_avoid_inds.append(i)
                            print("Unable to geocode avoid: " + avoid[i])
                    else:
                        avoided_already.append(avoid[i])

                        if len(coords) > 4:
                            coords = coords[::3]

                        for coord in coords:
                            avoided_locs.append(coord)

            if len(avoided_locs) > 0:
                avoid_str = "avoid="
                for i, loc in enumerate(avoided_locs):
                    avoid_str = avoid_str + "location:" + ",".join(map(str, loc))
                    if i < len(avoided_locs) - 1:
                        avoid_str += "|"
                avoid_str = avoid_str + "&"

        if bad_waypoint_inds is not None:
            for i in sorted(bad_waypoint_inds, reverse=True):
                del change_dict["waypoints"][i]

        if bad_avoid_inds is not None:
            for i in sorted(bad_avoid_inds, reverse=True):
                del change_dict["avoid"][i]

        change_dict["avoid_str"] = avoid_str
        change_dict["avoided_already"] = avoided_already
        change_dict["avoided_locs"] = avoided_locs
        update_changes_file(change_dict)

    url = f"https://api.geoapify.com/v1/routing?waypoints={','.join(map(str, start_coords))}|{more_waypoints}{','.join(map(str, end_coords))}&mode={path_type}&{avoid_str}details=route_details&apiKey={api_key}"
    result = requests.get(url)

    if result.status_code == 200:
        return result.json()
    else:
        return result.status_code