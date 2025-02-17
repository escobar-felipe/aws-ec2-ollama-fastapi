from fastapi import FastAPI, Request, Response, HTTPException, Depends
import httpx

# Configuração
OLLAMA_URL = "http://localhost:11434"
API_KEY = "demo"  # Token esperado

app = FastAPI()


async def validate_api_key(request: Request):
    """Valida o token Bearer"""
    auth_header = request.headers.get("Authorization")
    if auth_header != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(
    path: str, request: Request, _: None = Depends(validate_api_key)
):
    """Encaminha requisições para o Ollama"""

    # Monta a URL do destino
    target_url = f"{OLLAMA_URL}/api/{path}"

    # Define os headers originais (REMOVIDO O `Host`)
    headers = {
        key: value for key, value in request.headers.items() if key.lower() != "host"
    }

    async with httpx.AsyncClient() as client:
        # Lê o corpo da requisição
        body = await request.body()

        # Encaminha a requisição para o Ollama
        response = await client.request(
            method=request.method, url=target_url, headers=headers, content=body
        )

        # Verifica se é uma resposta de streaming
        if response.headers.get("content-type") == "text/event-stream":
            return Response(content=response.content, media_type="text/event-stream")

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
