# Ollama Custom Server for TinyLlama 1.1b

This repository provides a custom server that wraps the TinyLlama 1.1b model using Flask and Waitress. The server handles incoming requests, communicates with the `Ollama` API to generate completions, and returns the results in a custom format that you can configure. You can deploy this model and benchmark it using [`FMBench`](https://github.com/aws-samples/foundation-model-benchmarking-tool/tree/main).

## Prerequisites

- **Set up a Python 3.12 environment**: Set up the `python3.12` environment is not already using the commands below. If you are running this in the `FMBench` python environment, then this step is not needed:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    uv venv .tinyllama312 --python 3.12
    source .tinyllama312/bin/activate
    uv pip install -U Flask requests waitress
    ```

## Setup Instructions

1. In your terminal, configure the following environment variables used by the Ollama server to host the model:

    - `MODEL_NAME`: e.g., "tinyllama:1.1b"
    - `OLLAMA_ENDPOINT`: The URL endpoint for the Ollama API.
    - `AUTH_TOKEN`: Your secret token used to authenticate requests.
    - `DEFAULT_GENERATION_CONFIG`: Default settings for model generation (e.g., temperature, top_p).

    ```bash
    export OLLAMA_MODEL_NAME="tinyllama:1.1b"
    export OLLAMA_API_ENDPOINT="http://localhost:11434/api/generate"
    export OLLAMA_AUTH_TOKEN="your-secret-token-here"
    export OLLAMA_TEMPERATURE="0.3"
    export OLLAMA_TOP_P="0.3"
    ```

1. Creating the Model Configuration File: Before starting the server, you may need to create a model configuration file that tells Ollama how to load and configure your TinyLlama model.

    ```bash
        cat > Modelfile.tinyllama << EOL
    FROM tinyllama:1.1b
    PARAMETER temperature 0.3
    PARAMETER top_p 0.3
    SYSTEM "You are a helpful AI assistant specialized in personal information management and multilingual knowledge retrieval"
    EOL
    ```

1. Install Ollama:

    - For mac: 

        ```bash
        brew install ollama
        ```
    
    - For linux:

        ```bash
        curl -fsSL https://ollama.com/install.sh | sh
        ```

1. Create the tinyllama server:

    ```bash
    ollama create tinyllama -f Modelfile.tinyllama
    ```

1. Run the app:

    ```bash
    cd EC2_tinyllama/ollama_models/
    python app.py
    ```

1. Send a request to the model by using the following curl command:

    ```bash
    curl -X POST http://localhost:8080/v2/completions \
    -H "Content-Type: application/json" \
    -H "custom_authentication_token: your-secret-token-here" \
    -d '{
        "prompt": "What is machine learning?",
        "max_tokens": 512,
        "generation_config": {
        "temperature": 0.3,
        "top_p": 0.3
        }
    }'
    ```

### Benchmark Tinyllama on [`FMBench`](https://github.com/aws-samples/foundation-model-benchmarking-tool/tree/main)
---

To benchark Tinyllama on `FMBench`, follow the steps provided [here](https://aws-samples.github.io/foundation-model-benchmarking-tool/benchmarking_on_ec2.html#benchmarking-on-an-instance-type-with-nvidia-gpus-or-aws-chips) to launch an EC2 instance (this is tested on a `t3.xlarge` instance). Follow the commands above to spin up the tinyllama Ollama server. Use the following commands on your `FMBench` EC2 instance as follows:

1. Clone this repository:

    ```bash
    git clone https://github.com/madhurprash/EC2_tinyllama.git
    ```

1. ***Follow the commands above to set up tinyLlama on the `FMBench` instance. This can be done on the `FMBench` python environment.***

1. Benchmark the model using the following command:

    ```bash
    # Replace "/tmp" with "/path/to/your/custom/tmp" if you want to use a custom tmp directory
    TMP_DIR="/tmp"
    fmbench --config-file https://raw.githubusercontent.com/madhurprash/foundation-model-benchmarking-tool-old/refs/heads/main/fmbench/configs/byoe/config-byo-custom-rest-predictor-tinyllama.yml --local-mode yes --write-bucket placeholder --tmp-dir $TMP_DIR > fmbench.log 2>&1
    ```
