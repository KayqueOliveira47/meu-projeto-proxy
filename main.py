import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionamos a rota '/' e também mantemos a '/api/proxy' por garantia
@app.post("/")
@app.post("/api/proxy")
async def proxy_pluggy():
    # 1. Buscar credenciais das variáveis de ambiente da Vercel
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Variáveis de ambiente da Pluggy não configuradas.")

    # 2. Autenticar na API da Pluggy
    auth_url = "https://api.pluggy.ai/auth"
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret
    }
    
    auth_response = requests.post(auth_url, json=payload, headers={"Content-Type": "application/json"})
    
    if auth_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao autenticar com a Pluggy")
        
    api_token = auth_response.json().get("apiKey")
    
    # 3. Gerar o Connect Token para o Widget
    connect_token_url = "https://api.pluggy.ai/connect_token"
    connect_headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_token
    }
    
    token_res = requests.post(connect_token_url, json={}, headers=connect_headers)
    
    if token_res.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao gerar o connect token na Pluggy")

    return token_res.json()
