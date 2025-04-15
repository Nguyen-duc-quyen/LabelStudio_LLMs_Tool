import abc
from abc import ABC #Abstract Base Class
import json
import openai
import copy
from utils.image_utils import encode_image
from utils.convert_utils import remove_first_and_last_line, check_json_valid

class Prompt(ABC):
    """
        Each prompt has a different type of query, thus we need different parsing strategies.
        Each class is a designed for a specific prompt
    """
    def __init__(self, origin=None, model=None):
        self.origin = origin
        self.model = model
        pass
    
    
    @abc.abstractmethod
    def query(self, *args, **kwargs):
        """
            Specific type of query method for each prompt
        """
        return NotImplemented
    
    
    @abc.abstractmethod
    def parse(self, *args, **kwargs):
        """
            Parse the output to specified template
        """
        return NotImplemented
    

class Prompt_1(Prompt):
    def __init__(self, origin=None, model=None):
        super().__init__(origin, model)
        self.prompt = """
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
    
    def query(self, client: openai.Client, image_path: str) -> str:
        response = client.chat.completions.create(
        model=self.model,
        messages=[
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": self.prompt },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image(image_path)}",
                        },
                    },
                ],
            }
        ],
    )
    
        #Print the response as a JSON string
        return response.choices[0].message.content
    
    def parse(self, output: str, result_template: dict):
        pruned_response = remove_first_and_last_line(output)
        json_response = json.loads(pruned_response)
        json_response = json_response[0]
        if not check_json_valid:
            return TypeError("The JSON format is incorrect!")
    
        template = copy.deepcopy(result_template)
    
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
            result["origin"] = self.origin
    
        return template

class Prompt_2(Prompt):
    def __init__(self, origin=None, model=None):
        super().__init__(origin, model)

        self.prompt = "Analyze this shoe image and return annotations as per JSON schema."

        self.system_msg = (
            "You are a visual assistant that analyzes images of shoes and classifies them based on predefined categories. "
            "Always return a JSON object that follows the provided schema exactly. Each field should contain a single string label."
        )

        enum_string = lambda options: {
            "type": "string",
            "enum": options
        }

        categories = {
            "Function": ["Daily", "Fashion", "Running", "Hiking", "Walking", "Soccer", "Basketball",
                         "Training", "Gym", "Golf", "Tennis", "Skateboard", "Snow", "Surfing", "Swimming", "Aqua", "Combat"],
            "Type": ["Sneakers", "Sports", "Trainers", "Dress Shoes", "Sandals", "Heels", "Pumps", "Boots", "Traditional", "Slipper"],
            "Main Color": ["Neutral tones", "Pastels", "Bright/Variant", "Dark/Moody", "Monochrome"],
            "Sub Color": ["Neutral tones", "Pastels", "Bright/Variant", "Dark/Moody", "Monochrome"],
            "Upper Structure": ["No Upper", "One-Piece Upper", "Multi-Piece Upper"],
            "Closure Type": ["Shoelace", "Slip-on", "Velcro", "Straps", "Buckle", "Zipper", "Hook and Loop", "Dial"],
            "Toe Shape": ["Round", "Pointed", "Square", "Almond"],
            "Heel Type": ["Flat", "Block", "Stiletto", "Wedge"]
        }
        
        self.schema = {
            "type": "object",
            "properties": {k: enum_string(v) for k, v in categories.items()},
            "required": list(categories.keys()),
            "additionalProperties": False
}

    def query(self, client: openai.Client, image_path: str) -> str:
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_msg},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encode_image(image_path)}",
                            },
                        },
                    ],
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "shoe_annotation",
                    "schema": self.schema,
                    "strict": True
                }
            }
        )

        return response.choices[0].message.content

    def parse(self, output: str, result_template: dict):
        json_response = json.loads(output)
        template = copy.deepcopy(result_template)

        for result in template["result"]:
            attr = result["from_name"]
            if attr.startswith("answer") and attr[-1].isdigit():
                index = int(attr[-1])
                keys = list(json_response.keys())
                if index - 1 < len(keys):
                    result["value"]["text"] = [json_response[keys[index - 1]]]
                    result["origin"] = self.origin

        return template
    
class Prompt_3(Prompt):
    def __init__(self, origin=None, model=None):
        super().__init__(origin, model)

        self.prompt = "Analyze this shoe image and return annotations as per JSON schema."

        self.system_msg = (
            "You are a visual assistant that analyzes shoe images and classifies them based on predefined categories. "
            "For each attribute, return an array of one or more applicable labels. Only use values from the provided schema and "
            "return a JSON object matching the schema exactly."
        )

        enum_vals = lambda options: {
            "type": "array",
            "items": {"type": "string", "enum": options}
        }

        categories = {
            "Function": ["Daily", "Fashion", "Running", "Hiking", "Walking", "Soccer", "Basketball",
                         "Training", "Gym", "Golf", "Tennis", "Skateboard", "Snow", "Surfing", "Swimming", "Aqua", "Combat"],
            "Type": ["Sneakers", "Sports", "Trainers", "Dress Shoes", "Sandals", "Heels", "Pumps", "Boots", "Traditional", "Slipper"],
            "Main Color": ["Neutral tones", "Pastels", "Bright/Variant", "Dark/Moody", "Monochrome"],
            "Sub Color": ["Neutral tones", "Pastels", "Bright/Variant", "Dark/Moody", "Monochrome"],
            "Upper Structure": ["No Upper", "One-Piece Upper", "Multi-Piece Upper"],
            "Closure Type": ["Shoelace", "Slip-on", "Velcro", "Straps", "Buckle", "Zipper", "Hook and Loop", "Dial"],
            "Toe Shape": ["Round", "Pointed", "Square", "Almond"],
            "Heel Type": ["Flat", "Block", "Stiletto", "Wedge"]
        }

        self.schema = {
            "type": "object",
            "properties": {k: enum_vals(v) for k, v in categories.items()},
            "required": list(categories.keys()),
            "additionalProperties": False
        }

    def query(self, client: openai.Client, image_path: str) -> str:
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_msg},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encode_image(image_path)}",
                            },
                        },
                    ],
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "shoe_annotation",
                    "schema": self.schema,
                    "strict": True
                }
            }
        )

        return response.choices[0].message.content

    def parse(self, output: str, result_template: dict):
        json_response = json.loads(output)
        template = copy.deepcopy(result_template)

        for result in template["result"]:
            attr = result["from_name"]
            if attr.startswith("answer") and attr[-1].isdigit():
                index = int(attr[-1])
                keys = list(json_response.keys())
                if index - 1 < len(keys):
                    key = keys[index - 1]
                    val = json_response[key]
                    if isinstance(val, list):
                        result["value"]["text"] = [", ".join(val)]
                    else:
                        result["value"]["text"] = [val]
                    result["origin"] = self.origin

        return template
    
class Prompt_Test(Prompt):
    """
        Dummy prompt class for testing purposes only.
    """
    def __init__(self, origin=None, model=None):
        super().__init__(origin, model)
    
    def query(self, client: openai.Client, image_path: str) -> str:
        return "This is for testing purposes only."
    
    def parse(self, output: str, result_template: dict):
        return result_template