import json
import os
import requests

def handler(request):
    """
    Função nativa padrão que a Vercel encontra automaticamente.
    O argumento 'request' (opcional no Python puro da Vercel) representa a requisição.
    """
    
    # 1. Tratar o CORS (Preflight para requisições vindas do Front-end)
    # Se o método for OPTIONS, retorna apenas os headers de liberação
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }

    # Garantir que aceitamos apenas POST para segurança do proxy
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': 'Método não permitido'
        }

    # 2. Buscar credenciais das variáveis de ambiente da Vercel
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    # 3. Autenticar na API da Pluggy
    auth_url = "https://api.pluggy.ai/auth"
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret
    }
    headers = {"Content-Type": "application/json"}
    
    auth_response = requests.post(auth_url, json=payload, headers=headers)
    
    if auth_response.status_code != 200:
        return {
            'statusCode': 500,
            'body': 'Erro ao autenticar com a Pluggy'
        }
        
    api_token = auth_response.json().get("apiKey")
    
    # 4. Gerar o Connect Token para o Widget
    connect_token_url = "https://api.pluggy.ai/connect_token"
    connect_headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_token
    }
    
    token_res = requests.post(connect_token_url, json={}, headers=connect_headers)
    
    # 5. Retornar a resposta estruturada no padrão que a Vercel espera
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(token_res.json())
    }
