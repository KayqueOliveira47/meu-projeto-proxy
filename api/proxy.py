import json
import os
import requests
from werkzeug.wrappers import Request, Response

@Request.application
def handler(request):
    # 1. Tratar CORS (Preflight)
    if request.method == 'OPTIONS':
        response = Response('', status=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if request.method != 'POST':
        return Response('Método não permitido', status=405)

    # 2. Pegar credenciais da Pluggy nas variáveis de ambiente da Vercel
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    # 3. Autenticação na Pluggy
    auth_url = "https://api.pluggy.ai/auth"
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret
    }
    headers = {"Content-Type": "application/json"}
    
    auth_response = requests.post(auth_url, json=payload, headers=headers)
    
    if auth_response.status_code != 200:
        return Response('Erro ao autenticar com a Pluggy', status=500)
        
    api_token = auth_response.json().get("apiKey")
    
    # 4. Gerar o Connect Token
    connect_token_url = "https://api.pluggy.ai/connect_token"
    connect_headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_token
    }
    
    token_res = requests.post(connect_token_url, json={}, headers=connect_headers)
    
    # 5. Retornar resposta em JSON para o seu Frontend
    response = Response(json.dumps(token_res.json()), status=200, mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
