from label_studio_sdk import Client, Project
import json
import logging
from tqdm import tqdm
import os
import yaml


def initialize_client(url: str, api_key: str) -> Client:
    """Initialize Label Studio Client

    Args:
        url (str): url to the label studio server
        api_key (str): api key of the label studio server

    Returns:
        Client: Client object
    """
    return Client(url=url, api_key=api_key)


def update_prediction(project: Project ,prediction_id: int, prediction: dict):
    """Update prediction on label studio

    Args:
        project: Label Studio Project object
        prediction_id (int): Prediction ID
        prediction (dict): The actual prediction in JSON format
    """
    project.make_request("PATCH", "/api/predictions/{}".format(prediction_id), json=prediction)
    

def setup(config: dict, logger: logging.Logger):
    """Setup the project, get tasks' ids, result template
    
    Args:
        config: configuration dictionary
    """
    # Setup Label Studio Client
    ls_client = Client(url=config["label_studio_url"],
                       api_key=config["label_studio_api_key"])
    
    ls_project = ls_client.get_project(id=config["project_id"])
    
    # Get all images' urls from the Label Studio server
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
                image_file = image_file[9:]
                image_path = os.path.join(config["data_dir"], image_file)
                id2image_path[task["id"]] = image_path
    else:
        logger.error("Unsupported data storage format!")
        
    # Get the result template from file
    template_file = config["template"]
    with open(template_file) as f:
        template = json.load(f)
    
    return ls_project, tasks_list, id2image_path, template
    

# For testing purposes only
if __name__ == "__main__":
    config_file = "../configs/chat_gpt_40.yaml"
    
    # Load the config file
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    
    # Logging to terrminal
    logger = logging.getLogger("Label Studio LLM tool")
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False
    logger.setLevel(getattr(logging, config["logging"]))
    
    setup(config, logger)