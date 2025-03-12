import os
import json
import requests
from bs4 import BeautifulSoup

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

def get_cat_fact() -> str:
    """
    Fetches a single cat fact from the Cat Facts API.
    
    Returns:
        str: A random cat fact.
    """
    url = 'https://catfact.ninja/fact'
    params = {
        'limit': 1,
        'max_length': 140
    }
    headers = {
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data['fact']
    except requests.RequestException as e:
        return f"Error fetching cat fact: {str(e)}"
    
def get_exchange_rate(base_currency: str) -> float:
    response = requests.get(f'https://api.frankfurter.dev/v1/latest?base={base_currency}')
    data = response.json()
    return data

def scrape_website(url: str) -> str:
    """
    Scrapes the main content from a given website URL.
    
    Args:
        url (str): The URL of the website to scrape
        
    Returns:
        str: The scraped content or error message
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up text
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(lines)
        
        return f"Successfully scraped content from {url}:\n\n{text[:2000]}..." if len(text) > 2000 else text
        
    except Exception as e:
        return f"Error scraping website: {str(e)}"

