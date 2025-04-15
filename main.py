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
from utils.utils import *
from utils.label_studio_server import *
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Label Studio LLM pre-annotation tool', description="Get prediction from LLM and push it to Label Studio server")
    
    parser.add_argument("--config", type=str, help="System config", default="./configs/chat_gpt_40.yaml")
    args = parser.parse_args()
    
    
    # Read the configuration
    config_path = args.config
    with open(config_path, "r") as stream:
        config = yaml.safe_load(stream)
    
    
    # Logging to terrminal
    logger = logging.getLogger("Label Studio LLM tool")
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config["logging"]))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False
    logger.setLevel(getattr(logging, config["logging"]))
    

    #Defaults to 5 (might not be specified in the config file)
    MAX_RETRIES = config.get("MAX_RETRIES", 5)
        
    # Config OpenAI Client
    openai_client = OpenAI(api_key=config["openai_api_key"])
    
    prompt = create_prompt_from_config(config["prompt"])
    
    # Setup Label studio Client
    ls_project, tasks_list, id2image_path, template = setup(config, logger)
    
    logger.info("Getting the results from OpenAI ...")
    for index, task_id in tqdm(enumerate(list(id2image_path.keys())[:5])):
        image_path = id2image_path[task_id]
        retries = 0
        
        # Repeat the query until the result is valid
        while(retries < MAX_RETRIES):
            try:
                # Query using the prompt
                output = prompt.query(openai_client, image_path)
                # Parse the output 
                prediction = prompt.parse(output, template)
                
                if index == 0:
                    logger.debug("====================== DEBUGGING ======================")
                    logger.debug("Output: {}".format(output))
                    logger.debug("Prediction: {}".format(prediction))
                    logger.debug("Model: {}".format(prompt.model))
                    logger.debug("Origin: {}".format(prompt.origin))
                
                break # Successfully parsed the output, exit the loop
            except openai.BadRequestError as e:
                logger.error("Error in querying {}! Retrying {}".format(image_path, retries))
                logger.error(e)
                output = None
                prediction = None
                retries = MAX_RETRIES
                continue
            except Exception as e:
                logger.error("Error in querying {}! Retrying {}".format(image_path, retries))
                logger.error(type(e))
                output = None
                retries += 1
                continue
        else:
            logger.error("Failed to get the results from OpenAI after {} retries! Skipping the image.".format(MAX_RETRIES))
            continue
         
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
            ls_project.make_request("PATCH", "/api/predictions/{}".format(prediction_id), json=prediction)
        