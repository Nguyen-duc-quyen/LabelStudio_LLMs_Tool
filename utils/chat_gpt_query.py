import openai
import json
from .image_utils import encode_image


def get_annotation_for_local_image(client: openai.Client, image_path: str, prompt: str) -> str:
    """Get annotation from LLMs

    Args:
        image_url (str): link to the image
        

    Returns:
        str: _description_
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": prompt },
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