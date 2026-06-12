from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Buscar credenciais das variáveis de ambiente da Vercel
        client_id = os.environ.get("PLUGGY_CLIENT_ID")
        client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
        
        # 2. Autenticar na API da Pluggy para gerar o API Key/Token temporário
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
        
        # 3. Gerar um Connect Token para o Widget (Front-end) abrir com segurança
        # Se você já quiser pré-configurar para abrir direto no conector MeuPluggy:
        # Você pode passar o "connectorId" do MeuPluggy no options do payload se a API suportar,
        # ou gerenciar isso no front-end passando o ID do conector MeuPluggy.
        connect_token_url = "https://api.pluggy.ai/connect_token"
        connect_headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_token
        }
        
        # Opcional: restringir ou parametrizar o token
        connect_payload = {} 
        
        token_res = requests.post(connect_token_url, json=connect_payload, headers=connect_headers)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        # Libera CORS se o seu front-end estiver em outro domínio Vercel
        self.send_header('Access-Control-Allow-Origin', '*') 
        self.end_headers()
        
        self.wfile.write(json.dumps(token_res.json()).encode('utf-8'))
