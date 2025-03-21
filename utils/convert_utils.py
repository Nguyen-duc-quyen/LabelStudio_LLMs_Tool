import json


def convert_gpt2labelstudio(data: dict, img2id: dict) -> dict:
    """Convert result from chatGPT to label studio dictionary

    Args:
        data (dict): chatGPT dictionary format
        img2id (dict): convert image name to task_ids on label studio server

    Returns:
        dict: label studio dictionary
    """
    