import json
from utils import process_changes, instantiate_llm, get_changes_dict, init_changes_file, process_string, process_changes_ensemble
from routing import calc_route, check_route, codeAddress

from dotenv import load_dotenv
load_dotenv()

def evaluate_dataset(dataset_name, llm_num=1, temperature=0.0, top_p=1, open_ai=False):
    with open(f"project/datasets/{dataset_name}.json", "r") as file:
        dataset = json.load(file)

    llm = instantiate_llm(temperature=temperature, top_p=top_p, open_ai=open_ai)

    single_num_correct = 0
    single_num_include = 0
    single_num_miss = 0
    single_num_extra = 0

    single_num_route_good = 0

    for test in dataset["single"]:
        init_changes_file()

        correct = False
        include = False
        miss = False
        extra = False

        input = test["modification"]
        print("-----------------------------")
        print("Input: " + input)

        if llm_num == 1:
            process_changes(input, llm)
        else:
            process_changes_ensemble(input, llm, llm_num)

        change_dict = get_changes_dict()

        print("Change dict: " + str(change_dict))

        if test["waypoints"] != None:
            processed_test_waypoints = [process_string(waypoint) for waypoint in test["waypoints"]]
            processed_change_waypoints = [process_string(waypoint) for waypoint in change_dict["waypoints"]]
            if processed_test_waypoints == processed_change_waypoints:
                correct=True
            else:
                for waypoint in processed_test_waypoints:
                    if waypoint not in processed_change_waypoints:
                        miss=True
                        break
                if not miss:
                    include = True
        else:
            if len(change_dict["waypoints"]) != 0:
                extra=True

        if test["avoid"] != None:
            processed_test_avoid = [process_string(avoid) for avoid in test["avoid"]]
            processed_change_avoid = [process_string(avoid) for avoid in change_dict["avoid"]]
            if processed_test_avoid == processed_change_avoid:
                correct=True
            else:
                for avoid in processed_test_avoid:
                    if avoid not in processed_change_avoid:
                        miss=True
                        break
                if not miss:
                    include = True
        else:
            if len(change_dict["avoid"]) != 0:
                extra=True

        if test["path_type"] != None:
            if test["path_type"] == change_dict["path_type"]:
                correct=True
            else:
                miss=True
        else:
            if change_dict["path_type"] != "":
                extra=True

        if correct == True:
            single_num_correct += 1
            print("Correct")
        if include == True:
            single_num_include += 1
            print("Include")
        if miss == True:
            single_num_miss += 1
            print("Miss")
        if extra == True:
            single_num_extra += 1
            print("Extra")

        print("-----------------------------")

        route_good = True

        route = calc_route(test["start"], test["end"], test["bounds"])

        if test["avoid"] is not None:
            for avoid in test["avoid"]:
                exists = check_route(route, avoid) != []
                if exists:
                    print("Did not avoid " + avoid)
                    route_good = False
        
        if test["waypoints"] is not None:
            for waypoint in test["waypoints"]:
                waypoint_found = False
                loc = codeAddress(waypoint, test["bounds"])
                if len(route["properties"]["waypoints"]) > 2: 
                    for result_loc in route["properties"]["waypoints"][1:-1]:
                        if result_loc["lat"] == loc[0] and result_loc["lon"] == loc[1]:
                            waypoint_found = True
                            break
                if not waypoint_found:
                    print("Did not include " + waypoint)
                    route_good = False

        if test["path_type"] is not None:
            mode = route["properties"]["mode"]
            if test["path_type"] is not None and test["path_type"] != mode:
                print("Did not prefer " + test["path_type"])
                route_good = False


        if route_good:
            single_num_route_good += 1
            print("Route good")
        else:
            print("Route bad")

        print("-----------------------------")



    num_correct = 0
    num_include = 0
    num_miss = 0
    num_route_good = 0

    for test in dataset["multi"]:
        init_changes_file()

        input = test["modification"]
        print("-----------------------------")
        print("Input: " + input)

        if llm_num == 1:
            process_changes(input, llm)
        else:
            process_changes_ensemble(input, llm, llm_num)

        change_dict = get_changes_dict()

        print("Change dict: " + str(change_dict))

        processed_test_waypoints = [process_string(waypoint) for waypoint in test["waypoints"]]
        processed_change_waypoints = [process_string(waypoint) for waypoint in change_dict["waypoints"]]
        processed_test_avoid = [process_string(avoid) for avoid in test["avoid"]]
        processed_change_avoid = [process_string(avoid) for avoid in change_dict["avoid"]]

        if processed_test_waypoints == processed_change_waypoints:
            num_correct+=1
            print("Correct")
        else:
            miss = False
            for waypoint in processed_test_waypoints:
                if waypoint not in processed_change_waypoints:
                    num_miss+=1
                    miss = True
                    print("Miss")
                    break
            if not miss:
                num_include += 1
                print("Include")

        if processed_test_avoid == processed_change_avoid:
            num_correct+=1
            print("Correct")
        else:
            miss = False
            for avoid in processed_test_avoid:
                if avoid not in processed_change_avoid:
                    miss = True
                    num_miss+=1
                    print("Miss")
                    break
            if not miss:
                num_include += 1
                print("Include")

        if test["path_type"] == change_dict["path_type"]:
            num_correct+=1
            print("Correct")
        else:
            num_miss+=1
            print("Miss")

        print("-----------------------------")

        route_good = True

        route = calc_route(test["start"], test["end"], test["bounds"])

        for avoid in test["avoid"]:
            exists = check_route(route, avoid) != []
            if exists:
                print("Did not avoid " + avoid)
                route_good = False
        
        for waypoint in test["waypoints"]:
            waypoint_found = False
            loc = codeAddress(waypoint, test["bounds"])
            if len(route["properties"]["waypoints"]) > 2: 
                for result_loc in route["properties"]["waypoints"][1:-1]:
                    if result_loc["lat"] == loc[0] and result_loc["lon"] == loc[1]:
                        waypoint_found = True
                        break
            if not waypoint_found:
                print("Did not include " + waypoint)
                route_good = False

        mode = route["properties"]["mode"]
        if test["path_type"] is not None and test["path_type"] != mode:
            print("Did not prefer " + test["path_type"])
            route_good = False


        if route_good:
            num_route_good += 1
            print("Route good")
        else:
            print("Route bad")

        print("-----------------------------")

    print("SINGLE SUMMARY")
    print("-----------------------------")
    print("Correct: " + str(single_num_correct) + "/" + str(len(dataset["single"])))
    print("Include: " + str(single_num_include) + "/" + str(len(dataset["single"])))
    print("Miss: " + str(single_num_miss) + "/" + str(len(dataset["single"])))
    print("Extra: " + str(single_num_extra) + "/" + str(len(dataset["single"])))
    print("Route Good: " + str(single_num_route_good) + "/" + str(len(dataset["single"])))
    print("-----------------------------")

    print("-----------------------------")
    print("MULTI SUMMARY")
    print("-----------------------------")
    print("Correct: " + str(num_correct) + "/" + str(len(dataset["multi"])*3))
    print("Include: " + str(num_include) + "/" + str(len(dataset["multi"])*3))
    print("Miss: " + str(num_miss) + "/" + str(len(dataset["multi"])*3))
    print("Route Good: " + str(num_route_good) + "/" + str(len(dataset["multi"])))



if __name__ == "__main__":
    # 7 0.4
    evaluate_dataset("simple", open_ai=False, llm_num=15, temperature=0.05, top_p=1)


