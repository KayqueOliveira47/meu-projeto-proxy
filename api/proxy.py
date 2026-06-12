import os
import json
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Rota que lida com o Proxy e também gerencia o CORS automaticamente
# Mude de @app.route('/api/proxy', ...) para apenas '/'
@app.route('/', methods=['POST', 'OPTIONS'])
def proxy_pluggy():
    # ... resto do código igual ...
    # 1. Trata o Preflight request do CORS
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        headers = response.headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # 2. Buscar credenciais das variáveis de ambiente da Vercel
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    # 3. Autenticar na API da Pluggy
    auth_url = "https://api.pluggy.ai/auth"
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret
    }
    auth_headers = {"Content-Type": "application/json"}
    
    auth_response = requests.post(auth_url, json=payload, headers=auth_headers)
    
    if auth_response.status_code != 200:
        return jsonify({"error": "Erro ao autenticar com a Pluggy"}), 500
        
    api_token = auth_response.json().get("apiKey")
    
    # 4. Gerar o Connect Token para o MeuPluggy
    connect_token_url = "https://api.pluggy.ai/connect_token"
    connect_headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_token
    }
    
    token_res = requests.post(connect_token_url, json={}, headers=connect_headers)
    
    # 5. Retornar a resposta com os headers de CORS para o Frontend
    res = jsonify(token_res.json())
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res, 200

# Fallback para caso a Vercel procure o handler no escopo global
handler = app
