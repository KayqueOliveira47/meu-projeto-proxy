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
@app.post("/api/proxy")
async def proxy_pluggy():
    # 1. Validação estrita das variáveis de ambiente
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500, 
            detail="Erro Interno: As variaveis PLUGGY_CLIENT_ID ou PLUGGY_CLIENT_SECRET nao foram configuradas no painel da Vercel."
        )

    # 2. Tentativa de Autenticação na Pluggy
    auth_url = "https://api.pluggy.ai/auth"
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret
    }
    
    try:
        auth_response = requests.post(auth_url, json=payload, headers={"Content-Type": "application/json"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha de conexao ao tentar contactar a API da Pluggy: {str(e)}")
    
    if auth_response.status_code != 200:
        # Se a Pluggy rejeitar as credenciais, capturamos a resposta real deles para você saber o motivo
        motivo = auth_response.text
        raise HTTPException(status_code=401, detail=f"Credenciais rejeitadas pela Pluggy. Resposta da API: {motivo}")
        
    api_token = auth_response.json().get("apiKey")
    
    # 3. Gerar o Connect Token para o Widget do MeuPluggy
    connect_token_url = "https://api.pluggy.ai/connect_token"
    connect_headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_token
    }
    
    try:
        token_res = requests.post(connect_token_url, json={}, headers=connect_headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao gerar connect token: {str(e)}")
    
    if token_res.status_code != 200:
        raise HTTPException(status_code=token_res.status_code, detail="A Pluggy recusou a geracao do Connect Token.")

    return token_res.json()
