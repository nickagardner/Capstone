import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request

from utils import (add_waypoints, avoid_area, 
                   prefer_path_type, update_changes_file, 
                   init_changes_file, get_changes_dict,
                   process_changes, instantiate_llm)
from routing import calc_route
from trails import find_nearby_trails
from chains import mod_or_trail, extract_trail_info

app = Flask(__name__)

llm = instantiate_llm()

@app.route('/', methods=["POST","GET"])
def index():
    if request.method == "POST":
        json = request.get_json()['data_dict']
        if json['clear'] == True:
            init_changes_file()
        elif json['todo'] != "":
            type = mod_or_trail(json['todo'], llm)
            if type == "Trail":
                details = extract_trail_info(json['todo'], llm)
                return find_nearby_trails(json["start"], json["bounds"], details), 201
            else:
                process_changes(json["todo"], llm)
            
        start = json["start"]
        end = json["end"]
        bounds = json["bounds"]
        print(bounds)
        return calc_route(start, end, bounds), 200
    else:
        init_changes_file()
        
    return render_template('index.html', 
                            google_maps_string=f"https://maps.googleapis.com/maps/api/js?key={os.environ['GOOGLE_MAPS_API_KEY']}&libraries=places&callback=initMap")


if __name__ == "__main__":
   app.run(port=5001)