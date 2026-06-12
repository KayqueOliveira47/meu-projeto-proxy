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

# 1. ROTA GET (Front-end): Renderiza a página com o Widget da Pluggy
@app.get("/", response_class=HTMLResponse)
async def carregar_front():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Conector MeuPluggy</title>
        <script src="https://cdn.pluggy.ai/pluggy-connect/v2/pluggy-connect.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                background-color: #f4f5f7;
                margin: 0;
            }
            .btn-conectar {
                background-color: #0057FF;
                color: white;
                border: none;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: background 0.2s;
            }
            .btn-conectar:hover {
                background-color: #0042C2;
            }
            #status {
                margin-top: 20px;
                color: #555;
                font-size: 14px;
            }
        </style>
    </head>
    <body>

        <h1>Integração Open Finance</h1>
        <p>Clique no botão abaixo para conectar sua conta do MeuPluggy.</p>
        <button class="btn-conectar" onclick="abrirWidgetPluggy()">Conectar Conta Bancária</button>
        <div id="status"></div>

        <script>
            async function abrirWidgetPluggy() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerText = "Gerando token seguro...";

                try {
                    // 1. Busca o accessToken gerado pelo nosso próprio Proxy Python
                    const response = await fetch('/api/proxy', { method: 'POST' });
                    const data = await response.json();
                    
                    if (!data.accessToken) {
                        throw new Error("Token não encontrado na resposta do servidor.");
                    }

                    statusDiv.innerText = "Abriando o seletor de bancos...";

                    // 2. Inicializa o Widget da Pluggy na tela
                    const pluggyConnect = new PluggyConnect({
                        connectToken: data.accessToken,
                        // Força o widget a abrir direto no conector do MeuPluggy (ID 4)
                        connectorId: 4, 
                        onSuccess: (itemData) => {
                            // ISSO TRAZ A CONTA PARA O FRONT-END!
                            console.log('Sucesso! Conta conectada:', itemData);
                            statusDiv.innerHTML = `<b style="color: green;">Sucesso!</b> ID da Conexão: ${itemData.item.id}`;
                            
                            // Aqui você pode enviar o itemData.item.id de volta para o seu banco de dados se quiser
                        },
                        onError: (error) => {
                            console.error('Erro no widget da Pluggy:', error);
                            statusDiv.innerHTML = `<b style="color: red;">Erro na conexão:</b> ${error.message || error}`;
                        }
                    });

                    // Abre o painel visual
                    pluggyConnect.init();

                } catch (error) {
                    console.error('Erro ao iniciar o processo:', error);
                    statusDiv.innerHTML = `<b style="color: red;">Erro:</b> Não foi possível carregar o conector.`;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# 2. ROTA POST (Backend): O seu proxy que gera o Token (Já validado)
@app.post("/api/proxy")
async def proxy_pluggy():
    client_id = os.environ.get("PLUGGY_CLIENT_ID")
    client_secret = os.environ.get("PLUGGY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Variáveis de ambiente da Pluggy não configuradas.")

    auth_url = "https://api.pluggy.ai/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    
    auth_response = requests.post(auth_url, json=payload, headers={"Content-Type": "application/json"})
    if auth_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao autenticar com a Pluggy")
        
    api_token = auth_response.json().get("apiKey")
    
    connect_token_url = "https://api.pluggy.ai/connect_token"
    token_res = requests.post(connect_token_url, json={}, headers={"Content-Type": "application/json", "X-API-KEY": api_token})
    
    return token_res.json()
