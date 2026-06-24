# Forçando redeploy definitivo 2026
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

@app.post("/")
@app.get("/")
async def proxy_pluggy():
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Variáveis de ambiente não configuradas na Vercel.")

    # PASSO 1: Autenticar para pegar a API KEY mestre
    auth_url = "https://api.pluggy.ai/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    
    auth_response = requests.post(auth_url, json=payload, headers={"Content-Type": "application/json"})
    if auth_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao autenticar com a Pluggy (Passo 1)")
        
    api_token = auth_response.json().get("apiKey")
    
    # PASSO 2: Usar a API KEY para gerar o CONNECT TOKEN (Este vai para o Front-end)
    connect_token_url = "https://api.pluggy.ai/connect_token"
    
    # IMPORTANTE: A v2 da Pluggy exige o X-API-KEY no cabeçalho
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_token
    }
    
    # Opcional: Se quiser restringir as permissões do widget, pode passar opções no JSON aqui
    token_res = requests.post(connect_token_url, json={}, headers=headers)
    
    if token_res.status_code != 200:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao gerar Connect Token (Passo 2). Status: {token_res.status_code} - Resp: {token_res.text}"
        )
    
    # A resposta correta da Pluggy expõe o campo 'accessToken'
    dados_pluggy = token_res.json()
    
    # Garantimos que estamos devolvendo exatamente o token de acesso público
    return {"accessToken": dados_pluggy.get("accessToken")}
