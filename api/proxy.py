import json
import os
import requests
from http.server import BaseHTTPRequestHandler

class ProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Buscar credenciais das variáveis de ambiente da Vercel
        client_id = os.environ.get("PLUGGY_CLIENT_ID")
        client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
        
        # 2. Autenticar na API da Pluggy
        auth_url = "https://api.pluggy.ai/auth"
        payload = {
            "clientId": client_id,
            "clientSecret": client_secret
        }
        headers = {"Content-Type": "application/json"}
        
        auth_response = requests.post(auth_url, json=payload, headers=headers)
        
        if auth_response.status_code != 200:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Erro ao autenticar com a Pluggy")
            return
            
        api_token = auth_response.json().get("apiKey")
        
        # 3. Gerar o Connect Token para o Widget
        connect_token_url = "https://api.pluggy.ai/connect_token"
        connect_headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_token
        }
        
        token_res = requests.post(connect_token_url, json={}, headers=connect_headers)
        
        # 4. Resposta para o seu Frontend
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') 
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(token_res.json()).encode('utf-8'))

    def do_OPTIONS(self):
        # Trata o preflight request do CORS se o front estiver em outro domínio
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# A Vercel procura por essa variável 'handler' mapeada como a classe que gerencia a requisição
handler = ProxyHandler
