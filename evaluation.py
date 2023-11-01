import json
from chains import choose_func, split_changes
from utils import process_changes, instantiate_llm, get_changes_dict, init_changes_file, process_string

def evaluate_dataset(dataset_name):
    with open(f"project/datasets/{dataset_name}.json", "r") as file:
        dataset = json.load(file)

    llm = instantiate_llm()

    num_correct = 0
    num_include = 0
    num_miss = 0
    num_extra = 0

    for test in dataset["single"]:
        init_changes_file()

        correct = False
        include = False
        miss = False
        extra = False

        input = test["modification"]
        print("-----------------------------")
        print("Input: " + input)

        process_changes(input, llm)

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
            num_correct += 1
            print("Correct")
        if include == True:
            num_include += 1
            print("Include")
        if miss == True:
            num_miss += 1
            print("Miss")
        if extra == True:
            num_extra += 1
            print("Extra")

        print("-----------------------------")

    print("SINGLE SUMMARY")
    print("-----------------------------")
    print("Correct: " + str(num_correct))
    print("Include: " + str(num_include))
    print("Miss: " + str(num_miss))
    print("Extra: " + str(num_extra))
    print("-----------------------------")
    print("Total: " + str(len(dataset["single"])))


    num_correct = 0
    num_include = 0
    num_miss = 0

    for test in dataset["multi"]:
        init_changes_file()

        input = test["modification"]
        print("-----------------------------")
        print("Input: " + input)

        process_changes(input, llm)

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
    print("MULTI SUMMARY")
    print("-----------------------------")
    print("Correct: " + str(num_correct))
    print("Include: " + str(num_include))
    print("Miss: " + str(num_miss))
    print("-----------------------------")
    print("Total: " + str(len(dataset["multi"])*3))



if __name__ == "__main__":
    evaluate_dataset("simple")


