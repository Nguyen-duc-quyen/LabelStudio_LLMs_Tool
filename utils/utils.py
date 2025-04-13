import json
import importlib


def create_prompt_from_config(prompt_config) -> object:
    """Create a prompt object from the config file.

    Args:
        config (dict): configuration dictionary

    Returns:
        object: Prompt object
    """
    class_path = prompt_config
    module_name, class_name = class_path.rsplit('.', 1)
    
    # Import the module dynamically
    module = importlib.import_module(module_name)
    
    # Get the class from the module
    prompt_class = getattr(module, class_name)
    
    # Create an instance of the class
    prompt_instance = prompt_class()
    
    return prompt_instance