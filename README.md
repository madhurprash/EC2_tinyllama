# Ollama Custom Server for TinyLlama 1.1b

This repository provides a custom server that wraps the TinyLlama 1.1b model using Flask and Waitress. The server handles incoming requests, communicates with the Ollama API to generate completions, and returns the results in a custom format that you can configure.

## Prerequisites

- **Set up a Python 3.12 environment**: Set up the `python3.12` environments using the commands below:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    uv venv .tinyllama312 --python 3.12
    source .tinyllama312/bin/activate
    uv pip install -U Flask requests waitress
    ```

## Setup Instructions

1. Open the globals.py file and ensure the following settings are properly configured:

    - `MODEL_NAME`: e.g., "tinyllama:1.1b"
    - `OLLAMA_ENDPOINT`: The URL endpoint for the Ollama API.
    - `AUTH_TOKEN`: Your secret token used to authenticate requests.
    - `DEFAULT_GENERATION_CONFIG`: Default settings for model generation (e.g., temperature, top_p).

1. Creating the Model Configuration File: Before starting the server, you may need to create a model configuration file that tells Ollama how to load and configure your TinyLlama model.

    ```bash
    cat > Modelfile.tinyllama << EOL
    FROM tinyllama:1.1b
    PARAMETER temperature 0.3
    PARAMETER top_p 0.3
    SYSTEM You are a helpful AI assistant specialized in personal information management and multilingual knowledge retrieval
    EOL
    ```

1. Create the tinyllama server:

    ```bash
    ollama create tinyllama -f Modelfile.tinyllama
    ```

1. Run the app:

    ```bash
    python app.py
    ```

1. Send a request to the model by using the following curl command:

    ```bash
    curl -X POST http://localhost:8080/v2/completions -H "Content-Type: application/json" -H "custom_authentication_token: <your-auth-token>" -d '{
        "prompt": "What is machine learning?",
        "max_tokens": 512,
        "generation_config": {
            "temperature": 0.3,
            "top_p": 0.3
        }
    ```