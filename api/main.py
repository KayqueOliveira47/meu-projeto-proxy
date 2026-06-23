import os
import requests
from fastapi import FastAPI, HTTPException, Request
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

# Uma única rota mapeia a raiz global para TODOS os métodos (GET e POST)
@app.api_route("/", methods=["GET", "POST"])
async def gerenciar_tudo(request: Request):
    
    # -------------------------------------------------------------
    # SE FOR REQUISIÇÃO GET: Carrega o design com o botão azul
    # -------------------------------------------------------------
    if request.method == "GET":
        html_content = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Conector MeuPluggy</title>
            <script src="https://cdn.pluggy.ai/pluggy-connect/v2/index.js"></script>
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
                    
                    if (typeof window.PluggyConnect === 'undefined') {
                        statusDiv.innerHTML = `<b style="color: red;">Erro:</b> A biblioteca da Pluggy não carregou.`;
                        return;
                    }

                    statusDiv.innerText = "Gerando token seguro...";

                    try {
                        // FORÇA O DISPARO EXCLUSIVO NA RAIZ DO DOMÍNIO ATUAL (Sem sub-rotas)
                        const response = await fetch('/', { method: 'POST' });
                        
                        if (!response.ok) {
                            throw new Error(`Erro na rota do proxy: Status ${response.status}`);
                        }
                        
                        const data = await response.json();
                        
                        if (!data.accessToken) {
                            throw new Error("Token não encontrado na resposta.");
                        }

                        statusDiv.innerText = "Abrindo o MeuPluggy...";

                        const pluggyConnect = new window.PluggyConnect({
                            connectToken: data.accessToken,
                            connectorId: 4, 
                            onSuccess: (itemData) => {
                                console.log('Sucesso! Conta conectada:', itemData);
                                statusDiv.innerHTML = `<b style="color: green;">Sucesso!</b> ID da Conexão: ${itemData.item.id}`;
                            },
                            onError: (error) => {
                                console.error('Erro no widget:', error);
                                statusDiv.innerHTML = `<b style="color: red;">Erro no widget:</b> ${error.message || error}`;
                            }
                        });

                        pluggyConnect.init();

                    } catch (error) {
                        console.error('Erro:', error);
                        statusDiv.innerHTML = `<b style="color: red;">Erro:</b> ${error.message}`;
                    }
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)

    # -------------------------------------------------------------
    # SE FOR REQUISIÇÃO POST: O Botão foi clicado, gera o token
    # -------------------------------------------------------------
    elif request.method == "POST":
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
