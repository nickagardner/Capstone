import json
from utils import process_changes, instantiate_llm, get_changes_dict, init_changes_file, process_string
from routing import calc_route, check_route, codeAddress
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

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

        process_changes(input, llm, llm_num)

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
                        try:
                            if result_loc["lat"] == loc[0] and result_loc["lon"] == loc[1]:
                                waypoint_found = True
                                break
                        except:
                            pass
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

        process_changes(input, llm, llm_num)

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
                    try:
                        if result_loc["lat"] == loc[0] and result_loc["lon"] == loc[1]:
                            waypoint_found = True
                            break
                    except:
                        pass
            if not waypoint_found:
                print("Did not include " + waypoint)
                route_good = False

        if len(route["properties"]["waypoints"][1:-1]) != len(processed_change_waypoints):
            print("Wrong number of waypoints")
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

    del llm

    return {
        "single": {
            "correct": single_num_correct,
            "include": single_num_include,
            "miss": single_num_miss,
            "extra": single_num_extra,
            "route_good": single_num_route_good,
            "total": len(dataset["single"])
        },
        "multi": {
            "correct": num_correct,
            "include": num_include,
            "miss": num_miss,
            "route_good": num_route_good,
            "total": len(dataset["multi"])
        }
    }


def plot_evaluation():
    with open("ensemble_eval.json", "r") as file:
        eval_dict = json.load(file)

    consolidated_dict = {}
    for key in eval_dict:
        if key.split("_")[0] not in consolidated_dict:
            consolidated_dict[key.split("_")[0]] = {}
        consolidated_dict[key.split("_")[0]][key.split("_")[1]] = eval_dict[key]

    max_single = max([consolidated_dict[llm_num][temperature]["single"]["miss"] for llm_num in consolidated_dict for temperature in consolidated_dict[llm_num]]) + 1
    max_multi = max([consolidated_dict[llm_num][temperature]["multi"]["miss"] for llm_num in consolidated_dict for temperature in consolidated_dict[llm_num]]) + 1

    include_patch = mpatches.Patch(color='gold', label='Include') 
    miss_patch = mpatches.Patch(color='C3', label='Miss')
    extra_patch = mpatches.Patch(color='C1', label='Extra')
    comparison_patch = Line2D([0], [0], color="grey", linewidth=3, linestyle='--', label="Single Model")
    
    for llm_num in consolidated_dict:
        for type in ["single", "multi"]:
            fig, ax = plt.subplots()
            temperatures = [key for key in consolidated_dict[llm_num]]
            for idx, temperature in enumerate(temperatures):
                ax.bar(idx - 0.1, consolidated_dict[llm_num][temperature][type]["include"], color="gold", width=0.1)
                ax.bar(idx, consolidated_dict[llm_num][temperature][type]["miss"], color="C3", width=0.1)

                if type == "single":
                    ax.bar(idx + 0.1, consolidated_dict[llm_num][temperature][type]["extra"], color="C1", width=0.1)

                    ax.axhline(y=0, xmin=0, xmax=len(temperatures), color="gold", linestyle="--")
                    ax.axhline(y=3, xmin=0, xmax=len(temperatures), color="C3", linestyle="--")
                    ax.axhline(y=1, xmin=0, xmax=len(temperatures), color="C1", linestyle="--")

                else:
                    ax.axhline(y=0, xmin=0, xmax=len(temperatures), color="gold", linestyle="--")
                    ax.axhline(y=5, xmin=0, xmax=len(temperatures), color="C3", linestyle="--")

            if type == "single":
                max_y = max_single
            else:
                max_y = max_multi

            if type == "single":
                ax.legend(handles=[miss_patch, include_patch, extra_patch, comparison_patch])
            else:
                ax.legend(handles=[miss_patch, include_patch, comparison_patch])
            ax.set(xlabel="Temperature", ylabel="Count", title=f"{type.capitalize()} Tests Model Output Evaluation | {llm_num} LLM Ensemble",
                xticks=np.arange(len(temperatures)), xticklabels=temperatures, ylim=[-1,max_y])
            
            fig.savefig(f"project/images/{type}_{llm_num}_model_eval.png", bbox_inches='tight', dpi=300)

            plt.show()

    colors = ["C1", "C3", "C4"]
    markers = ["o", "s", "^"]
    for type in ["single", "multi"]:
        fig, ax = plt.subplots()
        idx = 0
        for llm_num in consolidated_dict:
            temperatures = [key for key in consolidated_dict[llm_num]]
            error_percs = []
            for temperature in temperatures:
                error_percs.append(((consolidated_dict[llm_num][temperature][type]["total"] - consolidated_dict[llm_num][temperature][type]["route_good"]) / consolidated_dict[llm_num][temperature][type]["total"]) * 100)

            ax.plot(np.arange(len(temperatures)), error_percs, color=colors[idx], marker=markers[idx], label=f"Ensemble | {llm_num} Models")

            idx += 1

        if type == "single":
            ax.axhline(y=8.33, xmin=0, xmax=len(temperatures), color="C0", linestyle="--", label="Single Model")
            ax.axhline(y=5, xmin=0, xmax=len(temperatures), color="C2", linestyle="--", label="ChatGPT")
        else:
            ax.axhline(y=25, xmin=0, xmax=len(temperatures), color="C0", linestyle="--", label="Single Model")
            ax.axhline(y=15, xmin=0, xmax=len(temperatures), color="C2", linestyle="--", label="ChatGPT")

        ax.set(xlabel="Temperature", ylabel="Failed Route Modifications (%)", title=f"{type.capitalize()} Tests Route Error Percentage | {llm_num} LLM Ensemble",
            xticks=np.arange(len(temperatures)), xticklabels=temperatures, ylim=[0,100])
        
        ax.legend()

        fig.savefig(f"project/images/{type}_route_eval.png", bbox_inches='tight', dpi=300)

        plt.show()



if __name__ == "__main__":
    # evaluate_dataset("simple", open_ai=False, llm_num=1, temperature=0.0, top_p=1)
    # plot_evaluation()
    overall_dict = {}
    for llm_num in [3, 5, 7]:
        for temperature in [0.05, 0.1, 0.2, 0.5, 1.0]:
            results_dict = evaluate_dataset("simple", open_ai=False, llm_num=llm_num, temperature=temperature, top_p=1)
            overall_dict[f"{llm_num}_{temperature}"] = results_dict
    print(overall_dict)

    with open("ensemble_eval_2.json", "w") as outfile: 
        json.dump(overall_dict, outfile)


