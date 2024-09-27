# Connected Agents Panel Application

This project is a Panel-based chat interface that uses AutoGen to create a multi-agent conversation system. It includes features like image generation, time checking, and cat fact retrieval.

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine.

### 2. Set Up a Python Virtual Environment

It's recommended to use a virtual environment to manage dependencies. Here's how to set it up:

### 3. Install Requirements

Install the required packages using pip:

```bash
pip install -r requirements.txt
```


### 4. Configure OAI_CONFIG_LIST

Create a file named `OAI_CONFIG_LIST` in the root directory of the project. This file should contain your OpenAI API configuration. Here's a template:

```json
[
    {
        "model": "gpt-4",
        "api_key": "<your OpenAI API key here>"
    },
    {
        "model": "<your Azure OpenAI deployment name>",
        "api_key": "<your Azure OpenAI API key here>",
        "base_url": "<your Azure OpenAI API base URL>",
        "api_type": "azure",
        "api_version": "<your Azure OpenAI API version here>"
    }
]
```

Replace the placeholders with your actual API details:
- `model`: The name of the model you're using (e.g., "gpt-4" for OpenAI, or your deployment name for Azure)
- `api_key`: Your API key for authentication
- `base_url`: The base URL for your Azure OpenAI API (only for Azure deployments)
- `api_type`: Set to "azure" for Azure OpenAI deployments
- `api_version`: The API version you're using with Azure OpenAI

### 5. Run the Panel Application

To start the Panel application, run:


This will start the server, and you should see output indicating the URL where the application is running (typically `http://localhost:5006`).

## Usage

Once the application is running, open a web browser and navigate to the URL provided (usually `http://localhost:5006`). You can then interact with the chat interface to engage with the various agents and tools available in the system.

## Features

- Multi-agent conversation system using AutoGen
- Image generation capabilities
- Current time retrieval
- Cat fact retrieval
- Interactive chat interface built with Panel

## License

This project is licensed under the MIT License. See the LICENSE file for details.