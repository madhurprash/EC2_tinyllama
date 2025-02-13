import os
import json
import time
import hmac
import globals
import logging
import hashlib
import requests
from globals import *
from flask import Flask, request, jsonify, abort

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Define the environment variables
MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME', 'tinyllama:1.1b')
OLLAMA_ENDPOINT = os.getenv('OLLAMA_API_ENDPOINT', 'http://localhost:11434/api/generate')
AUTH_TOKEN = os.getenv('OLLAMA_AUTH_TOKEN')

DEFAULT_GENERATION_CONFIG = {
    'temperature': float(os.getenv('OLLAMA_TEMPERATURE', '0.3')),
    'top_p': float(os.getenv('OLLAMA_TOP_P', '0.3'))
}


def verify_auth_token(request_token):
    if not hmac.compare_digest(request_token, AUTH_TOKEN):
        abort(401, description="Invalid authentication token")

@app.route('/v2/completions', methods=['POST'])
def predict():
    try:
        # Verify authentication
        auth_token = request.headers.get('custom_authentication_token')
        if auth_token:
            verify_auth_token(auth_token)
        
        # Get custom input format
        input_data = request.json
        logger.info(f"Received request type: {type(input_data)}")
        
        # Extract prompt from your custom format
        if 'prompt' in input_data:
            prompt = input_data['prompt']
        else:
            return jsonify({"error": "Missing 'prompt' field in request"}), 400
        
        # Get optional parameters
        system_prompt = input_data.get('system', "You are a helpful AI assistant")
        max_tokens = input_data.get('max_tokens', 512)
        
        # Extract generation config from request or use defaults
        generation_config = input_data.get('generation_config', {})
        temperature = generation_config.get('temperature', DEFAULT_GENERATION_CONFIG['temperature'])
        top_p = generation_config.get('top_p', DEFAULT_GENERATION_CONFIG['top_p'])
        
        # Prepare Ollama request with correct format
        ollama_payload = {
            "model": MODEL_NAME, 
            "prompt": prompt,
            "stream": False,
            "options": {        
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens
            }
        }
        
        logger.info(f"Sending request to Ollama for model: {MODEL_NAME}")
        logger.info(f"Payload: {ollama_payload}")  # Add this for debugging
        
        # Call Ollama API
        start_time = time.time()
        response = requests.post(OLLAMA_ENDPOINT, json=ollama_payload)
        response.raise_for_status()
        result = response.json()
        inference_time = time.time() - start_time
        
        # Transform to expected output format for /v2/completions endpoint
        output = {
            "id": f"cmpl-{os.urandom(4).hex()}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": MODEL_NAME,
            "choices": [
                {
                    "text": result['response'],
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": result.get('prompt_eval_count', 0),
                "completion_tokens": result.get('eval_count', 0),
            },
            "metadata": {
                "inference_time_seconds": round(inference_time, 3)
            }
        }
        logger.info(f"Request processed in {inference_time:.2f}s, generated {output['usage']['completion_tokens']} tokens")
        return jsonify(output)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # For production use on t3.xlarge with a 1B model
    from waitress import serve
    logger.info(f"Starting Ollama custom server for {MODEL_NAME} on port 8080...")
    serve(app, host='0.0.0.0', port=8080, threads=8)  # Reduced threads for 1B model