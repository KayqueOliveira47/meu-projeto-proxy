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

# Mantemos a raiz por segurança
@app.post("/")
@app.get("/")
async def raiz():
    return {"status": "operacional"}

# Mude de @app.post("/api/token") para apenas "/"
@app.post("/")
@app.get("/")
async def obter_connect_token():
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Variáveis não configuradas.")

    # 1. Busca API Key mestre
    auth_response = requests.post(
        "https://api.pluggy.ai/auth", 
        json={"clientId": client_id, "clientSecret": client_secret}
    )
    if auth_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro no Passo 1 da Pluggy")
        
    api_token = auth_response.json().get("apiKey")
    
    # 2. Gera o Connect Token legítimo
    token_res = requests.post(
        "https://api.pluggy.ai/connect_token", 
        json={}, 
        headers={"X-API-KEY": api_token}
    )
    
    if token_res.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro no Passo 2 da Pluggy")
    
    return {"accessToken": token_res.json().get("accessToken")}
