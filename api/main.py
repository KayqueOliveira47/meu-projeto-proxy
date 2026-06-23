import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# O CORS garante que seu site no GitHub Pages consiga conversar com a Vercel sem bloqueios
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/proxy")
@app.get("/api/proxy")
@app.api_route("/", methods=["GET", "POST", "OPTIONS"])
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
