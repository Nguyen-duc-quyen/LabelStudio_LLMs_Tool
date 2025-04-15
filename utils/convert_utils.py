import json
import copy
import pandas as pd


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


def flatten_annotation_json(input_json_path, output_csv_path=None, output_json_path=None):
    """
    Converts a nested annotation JSON (e.g., from Label Studio) into a flat tabular format.

    Parameters:
        input_json_path (str): Path to the input JSON file.
        output_csv_path (str): Optional path to save the output as CSV.
        output_json_path (str): Optional path to save the output as JSON.
    
    Returns:
        pd.DataFrame: Flattened annotations dataframe.
    """
    # Define question-to-answer mapping
    question_keys = {
        "q1": "answer1",
        "q2": "answer2",
        "q3": "answer3",
        "q4": "answer4",
        "q5": "answer5",
        "q6": "answer6",
        "q7": "answer7",
        "q8": "answer8"
    }

    # Load JSON
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    flattened_data = []

    for task in data:
        task_id = task["id"]
        image_path = task.get("data", {}).get("image", "")
        file_name = task.get("file_upload", "")

        # Assume one annotation per task
        annotation = task.get("annotations", [])[0]
        annotation_result = {item["to_name"]: item["value"]["text"][0] for item in annotation["result"]}

        # Get prediction embedded inside annotation
        prediction_result = {}
        prediction_created_at = None
        if "prediction" in annotation:
            prediction_obj = annotation["prediction"]
            prediction_created_at = prediction_obj.get("created_at")
            if "result" in prediction_obj:
                prediction_result = {item["to_name"]: item["value"]["text"][0] for item in prediction_obj["result"]}

        # Create record
        entry = {
            "task_id": task_id,
            "image_path": image_path,
            "file_name": file_name,
            "annotation_id": annotation["id"],
            "completed_by": annotation.get("completed_by"),
            #"lead_time": annotation.get("lead_time"),
            "annotation_created_at": annotation.get("created_at"),
            "annotation_updated_at": annotation.get("updated_at"),
            "parent_prediction_id": annotation.get("parent_prediction"),
            "prediction_created_at": prediction_created_at
        }

        # Add Q&A comparisons
        for q_key in question_keys:
            pred_value = prediction_result.get(q_key)
            anno_value = annotation_result.get(q_key)
            changed = (pred_value != anno_value) if pred_value is not None and anno_value is not None else None
            entry[f"{q_key}_prediction"] = pred_value
            entry[f"{q_key}_annotation"] = anno_value
            entry[f"{q_key}_changed"] = changed

        flattened_data.append(entry)

    # Convert to DataFrame
    df_flattened = pd.DataFrame(flattened_data)

    # Save to CSV
    if output_csv_path:
        df_flattened.to_csv(output_csv_path, index=False)
        print(f"Saved CSV to: {output_csv_path}")

    # Save to JSON
    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(flattened_data, f, ensure_ascii=False, indent=2)
        print(f"Saved JSON to: {output_json_path}")

    return df_flattened


if __name__ == "__main__":
    df = flatten_annotation_json(
        input_json_path="E:\\Code\\KAIST\\DEAL-ShoeDesign\\ChatGPT_ShoeGen\\annotations\\original_annotations\\project-6-at-2025-04-15-15-01-8521cc11.json",
        output_csv_path="E:\\Code\\KAIST\\DEAL-ShoeDesign\\ChatGPT_ShoeGen\\annotations\\formatted_annotations\\project-6-at-2025-04-15-15-01-8521cc11.csv",
        output_json_path="E:\\Code\\KAIST\\DEAL-ShoeDesign\\ChatGPT_ShoeGen\\annotations\\formatted_annotations\\project-6-at-2025-04-15-15-01-8521cc11.json"
    )

