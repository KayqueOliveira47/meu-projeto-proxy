import os
import json
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/proxy', methods=['POST', 'OPTIONS'])
def proxy_pluggy():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        headers = response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    auth_url = "https://api.pluggy.ai/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    
    auth_response = requests.post(auth_url, json=payload, headers={"Content-Type": "application/json"})
    if auth_response.status_code != 200:
        return jsonify({"error": "Erro ao autenticar com a Pluggy"}), 500
        
    api_token = auth_response.json().get("apiKey")
    
    connect_token_url = "https://api.pluggy.ai/connect_token"
    token_res = requests.post(connect_token_url, json={}, headers={"Content-Type": "application/json", "X-API-KEY": api_token})
    
    res = jsonify(token_res.json())
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res, 200
