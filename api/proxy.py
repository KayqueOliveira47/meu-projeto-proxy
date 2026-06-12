import json
import os
import requests

def handler(environ, start_response):
    # 1. Captura o método HTTP
    request_method = environ.get('REQUEST_METHOD', 'GET')

    # 2. Trata requisições CORS (Preflight)
    if request_method == 'OPTIONS':
        headers = [
            ('Content-Type', 'text/plain'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type')
        ]
        start_response('200 OK', headers)
        return [b'']

    # Bloqueia se não for POST
    if request_method != 'POST':
        headers = [('Content-Type', 'text/plain')]
        start_response('405 Method Not Allowed', headers)
        return [b'Metodo nao permitido']

    # 3. Credenciais da Pluggy nas variáveis de ambiente da Vercel
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    # 4. Autenticação na Pluggy
    auth_url = "https://api.pluggy.ai/auth"
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret
    }
    auth_headers = {"Content-Type": "application/json"}
    
    auth_response = requests.post(auth_url, json=payload, headers=auth_headers)
    
    if auth_response.status_code != 200:
        headers = [('Content-Type', 'text/plain')]
        start_response('500 Internal Server Error', headers)
        return [b'Erro ao autenticar com a Pluggy']
        
    api_token = auth_response.json().get("apiKey")
    
    # 5. Gerar o Connect Token
    connect_token_url = "https://api.pluggy.ai/connect_token"
    connect_headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_token
    }
    
    token_res = requests.post(connect_token_url, json={}, headers=connect_headers)
    
    # 6. Retornar resposta para o Frontend
    response_body = json.dumps(token_res.json()).encode('utf-8')
    
    headers = [
        ('Content-Type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]
    
    start_response('200 OK', headers)
    return [response_body]
