import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Rota GET: Lê o arquivo index.html da mesma pasta e entrega na tela
@app.get("/")
@app.get("/api/proxy")
async def carregar_front():
    # Encontra o caminho do index.html ao lado deste arquivo main.py
    current_dir = os.path.dirname(os.path.realpath(__file__))
    html_path = os.path.join(current_dir, "index.html")
    
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar HTML interno: {str(e)}")

# 2. Rota POST: Gera o token da Pluggy
@app.post("/")
@app.post("/api/proxy")
async def proxy_pluggy():
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Variáveis de ambiente não configuradas.")

    auth_url = "https://api.pluggy.ai/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    
    auth_response = requests.post(auth_url, json=payload, headers={"Content-Type": "application/json"})
    if auth_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao autenticar com a Pluggy")
        
    api_token = auth_response.json().get("apiKey")
    
    connect_token_url = "https://api.pluggy.ai/connect_token"
    token_res = requests.post(connect_token_url, json={}, headers={"Content-Type": "application/json", "X-API-KEY": api_token})
    
    return token_res.json()
