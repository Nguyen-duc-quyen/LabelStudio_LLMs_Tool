from label_studio_sdk import Client
import json


def initialize_client(url: str, api_key: str) -> Client:
    """Initialize Label Studio Client

    Args:
        url (str): url to the label studio server
        api_key (str): api key of the label studio server

    Returns:
        Client: Client object
    """
    return Client(url=url, api_key=api_key)


def upload_predictions(predictions: list):
    """Upload predictions from LLM to label studio

    Args:
        predictions (list): List of predictions in converted format
    """
    
    