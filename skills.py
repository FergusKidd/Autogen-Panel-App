import os
import json
import requests

from openai import AzureOpenAI
from typing import List

import datetime

def current_time():
    return datetime.datetime.now().isoformat()

def generate_and_save_images(query: str, image_size: str = "1024x1024") -> List[str]:
    
    #config:
    # Read the JSON file

    config_path = os.path.join(os.path.dirname(__file__), "OAI_CONFIG_LIST")

    with open(config_path) as f:
        config = json.load(f)


    client = AzureOpenAI(
        api_version="2024-05-01-preview",
        azure_endpoint=config['base_url'],
        api_key=config['api_key'],
    )

    result = client.images.generate(
        model="Dalle3", # the name of your DALL-E 3 deployment
        prompt=query,
        n=1
    )

    image_url = json.loads(result.model_dump_json())['data'][0]['url']

    #dowblaod to local files/images
    # Download the image
    response = requests.get(image_url)
    #create the file

    cwd = os.getcwd()
    image_path = f"{cwd}/generated_images/{query.replace(' ', '_')}.png"


    
    with open(image_path, "wb+") as file:
        file.write(response.content)

    return "IMAGE GENERATED: " + image_path
