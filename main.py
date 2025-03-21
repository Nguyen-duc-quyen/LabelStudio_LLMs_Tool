import json
import yaml
import argparse
import logging
from tqdm import tqdm
from openai import OpenAI
from label_studio_sdk import Client
import label_studio as ls
from utils.chat_gpt_query import *
from utils.convert_utils import *
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Label Studio LLM pre-annotation tool', description="Get prediction from LLM and push it to Label Studio server")
    
    parser.add_argument("--config", type=str, help="System config", default="./configs/chat_gpt_40.yaml")
    args = parser.parse_args()
    
    # Logging to terrminal
    logger = logging.getLogger("Label Studio LLM tool")
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    
    # Read the configuration
    config_path = args.config
    with open(config_path, "r") as stream:
        config = yaml.safe_load(stream)
        
    # Config OpenAI Client
    openai_client = OpenAI(api_key=config["openai_api_key"])
    
    prompt = """
    Analyze this shoe image and return structured annotations in JSON format using this schema:
    Condition = {"attribute": [str]}
    Return: list[Condition]
    Ensure attribute and value follows this mapping:
    "Function": ["Daily", "Fashion", "Running", "Hiking", "Walking", "Soccer", "Basketball",
                 "Training", "Gym", "Golf", "Tennis", "Skateboard", "Snow", "Surfing", "Swimming", "Aqua", "Combat"],
    "Type": ["Sneakers", "Sports", "Trainers", "Dress Shoes", "Sandals", "Heels", "Pumps", "Boots", "Traditional", "Slipper"],
    "Main Color": ["Neutral tones", "Pastels", "Bright/Variant", "Dark/Moody", "Monochrome"],
    "Sub Color": ["Neutral tones", "Pastels", "Bright/Variant", "Dark/Moody", "Monochrome"],
    "Upper Structure": ["No Upper", "One-Piece Upper", "Multi-Piece Upper"],
    "Closure Type": ["Shoelace", "Slip-on", "Velcro", "Straps", "Buckle", "Zipper", "Hook and Loop", "Dial"],
    "Toe Shape": ["Round", "Pointed", "Square", "Almond"],
    "Heel Type": ["Flat", "Block", "Stiletto", "Wedge"]
    The key should be a string corresponding to each of the attributes listed above.
    The value should be a list containing the corresponding labels from the provided categories
    Return only 1 JSON dictionary, which can be parsed using Python. Follow the possible values for each attribute and do not generate your own attributes.
    """
    
    # Config Label studio Client
    ls_client = Client(url=config["label_studio_url"], api_key=config["label_studio_api_key"])
    ls_project = ls_client.get_project(id=config["project_id"])
    
    # Get all images' urls from the server
    tasks_list = ls_project.get_tasks()
    id2image_path = {}
    
    logger.info("Getting all the image urls from project id: {}".format(config["project_id"]))
    # If the image are stored remotely
    if config["data_storage"] == "remote":
        for task in tqdm(tasks_list):
            if 'image' in task['data']:
                id2image_path[task["id"]] = config["label_studio_url"] + task['data'].get('image')
            else:
                continue
    elif config["data_storage"] == "local":
        for task in tqdm(tasks_list):
            if 'image' in task['data']:
                image_file = task['data'].get('image').split("/")[-1]
                image_file = image_file.split("-")[-1]
                image_path = os.path.join(config["data_dir"], image_file)
                id2image_path[task["id"]] = image_path
    else:
        logger.error("Unsupported data storage format!")
        
    # Get the result template
    template_file = config["template"]
    with open(template_file) as f:
        template = json.load(f)
    
    
    logger.info("Getting the results from OpenAI ...")
    for task_id in tqdm(list(id2image_path.keys())[:5]):
        image_path = id2image_path[task_id]
        llm_result = get_annotation_for_local_image(openai_client, image_path, prompt)
        
        # Convert to the desire format
        prediction = convert_gpt2labelstudio(data=llm_result, orig_template=template)
        
        # Check if the task has already have prediction
        predictions = ls_project.get_task(task_id)["predictions"]
        
        if len(predictions) == 0:
            # Create new prediction
            prediction = prediction["result"]
            response = ls_project.create_prediction(
                task_id=task_id,
                result=prediction
            )
        else:
            # Update the prediction
            prediction_id = predictions[0]["id"]
            ls_project.make_request("PATCH", "/api/predictions/{}".format(prediction_id), json=template)
        