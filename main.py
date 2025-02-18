from fastapi import FastAPI, Request, Response, HTTPException, Depends
import httpx
import logging
import asyncio

# Configurations
OLLAMA_URL = "http://0.0.0.0:11434"
API_KEY = "demo"  # Expected Bearer token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


async def validate_api_key(request: Request):
    """Validate Bearer Token"""
    auth_header = request.headers.get("Authorization")
    logger.info(f"Received Authorization header: {auth_header}")

    if auth_header != f"Bearer {API_KEY}":
        logger.warning("Unauthorized access attempt!")
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(
    path: str, request: Request, _: None = Depends(validate_api_key)
):
    """Proxy requests to Ollama, handling both normal and streaming responses"""

    logger.info(f"Incoming request: {request.method} /v1/{path}")

    # Construct target URL (remove redundant '/api/')
    target_url = f"{OLLAMA_URL}/{path}"
    logger.info(f"Forwarding request to: {target_url}")

    # Capture headers (excluding 'host')
    headers = {
        key: value for key, value in request.headers.items() if key.lower() != "host"
    }
    logger.info(f"Forwarding headers: {headers}")

    async with httpx.AsyncClient() as client:
        body = await request.body()
        logger.info(f"Request body: {body.decode() if body else 'No body'}")

        try:
            async with client.stream(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=60.0,  # Increase timeout to handle long responses
            ) as response:

                # Handle Streaming Response
                if response.headers.get("content-type") == "text/event-stream":
                    return Response(
                        content=stream_response(response),
                        media_type="text/event-stream",
                    )

                # Handle Normal Response
                return Response(
                    content=await response.aread(),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

        except httpx.RequestError as e:
            logger.error(f"Request to Ollama failed: {str(e)}")
            raise HTTPException(status_code=502, detail="Ollama backend unavailable")


async def stream_response(response):
    """Stream data from Ollama to the client"""
    async for chunk in response.aiter_bytes():
        yield chunk


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
