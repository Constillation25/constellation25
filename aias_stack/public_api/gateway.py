#!/usr/bin/env python3
"""
C25 Public API Gateway
OpenAI-compatible endpoint with FacePrintPay auth
"""
from flask import Flask, request, jsonify, stream_with_context
import json
import time

app = Flask(__name__)

# Import FacePrintPay auth
import sys
sys.path.append('../faceprintpay_gateway')
from biometric_auth import auth

# Rate limiting configuration
RATE_LIMITS = {
    "free": {"requests_per_min": 10, "tokens_per_day": 10000},
    "pro": {"requests_per_min": 100, "tokens_per_day": 1000000},
    "enterprise": {"requests_per_min": 1000, "tokens_per_day": -1}
}

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint"""
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not auth.validate_api_key(api_key):
        return jsonify({"error": "Invalid or expired API key"}), 401
    
    data = request.json
    model = data.get('model', 'c25-default')
    messages = data.get('messages', [])
    stream = data.get('stream', False)
    
    # Route to Chairman LLM for multi-agent evaluation
    response = {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "C25 Sovereign AI Response - Multi-agent evaluated"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(messages),
            "completion_tokens": 50,
            "total_tokens": len(messages) + 50
        }
    }
    
    return jsonify(response)

@app.route('/v1/models', methods=['GET'])
def list_models():
    """List available C25 models"""
    return jsonify({
        "object": "list",
        "data": [
            {"id": "c25-default", "object": "model", "created": 1720000000},
            {"id": "c25-code", "object": "model", "created": 1720000000},
            {"id": "c25-reasoning", "object": "model", "created": 1720000000}
        ]
    })

@app.route('/v1/enroll', methods=['POST'])
def enroll_biometric():
    """Enroll new user with biometric"""
    data = request.json
    user_id = data.get('user_id')
    biometric = data.get('biometric_signature')
    
    result = auth.enroll_biometric(biometric)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
