from googletrans import Translator, constants
import json

def translate_dataset(dataset_name):
    with open(f"project/datasets/{dataset_name}.json", "r") as file:
        dataset = json.load(file)

    translator = Translator()

    for test in dataset["multi"]:
        test_translate = translator.translate(test["modification"], dest="fr").text
        test_back = translator.translate(test_translate, dest="en").text
        print(test_back)

if __name__ == "__main__":
    translate_dataset("simple")