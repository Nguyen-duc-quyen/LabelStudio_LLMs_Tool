import json
import copy


def remove_first_and_last_line(text: str) -> str:
    """Remove the first and last line of the output of the LLM model so that it can be parsed as JSON object

    Args:
        text (str): LLM output

    Returns:
        str: The output string
    """
    lines = text.splitlines()  # Split into lines
    if len(lines) > 2:  # Ensure there are at least 3 lines to remove first and last
        return "\n".join(lines[1:-1])  # Join everything except first & last line
    return ""  # Return empty if there are not enough lines


def check_json_valid(json_data: dict) -> bool:
    """Check whether the json data is valid for submission

    Args:
        json_data (dict): json data

    Returns:
        bool: whether the json is valid
    """
    keys = [
        "Function", "Type", "Main Color", "Sub Color", "Upper Structure", "Closure Type", "Toe Shape", "Heel Type"
    ]
    for key in keys:
        if key not in json_data.keys():
            return False
    return True
    

def convert_gpt2labelstudio(data: str, orig_template: list) -> dict:
    """Convert result from chatGPT to label studio dictionary

    Args:
        data (str): chatGPT response
        template (list): the list of dictionaries in the desired format

    Returns:
        dict: label studio dictionary
    """
    pruned_response = remove_first_and_last_line(data)
    json_response = json.loads(pruned_response)
    json_response = json_response[0]
    if not check_json_valid:
        return TypeError("The JSON format is incorrect!")
    
    template = copy.deepcopy(orig_template)
    
    for result in template["result"]:
        if result["from_name"] == "answer1":
            result["value"]["text"] = [", ".join(json_response["Function"])]
        elif result["from_name"] == "answer2":
            result["value"]["text"] = [", ".join(json_response["Type"])]
        elif result["from_name"] == "answer3":
            result["value"]["text"] = [", ".join(json_response["Main Color"])]
        elif result["from_name"] == "answer4":
            result["value"]["text"] = [", ".join(json_response["Sub Color"])]
        elif result["from_name"] == "answer5":
            result["value"]["text"] = [", ".join(json_response["Upper Structure"])]
        elif result["from_name"] == "answer6":
            result["value"]["text"] = [", ".join(json_response["Closure Type"])]
        elif result["from_name"] == "answer7":
            result["value"]["text"] = [", ".join(json_response["Toe Shape"])]
        elif result["from_name"] == "answer8":
            result["value"]["text"] = [", ".join(json_response["Heel Type"])]
        else:
            continue
        result["origin"] = "ChatGPT"
    
    return template