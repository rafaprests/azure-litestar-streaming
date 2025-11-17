import azure.functions as func
import logging
from litapp import litapp

app = func.FunctionApp()

@app.route(route="{*path}", auth_level=func.AuthLevel.ANONYMOUS)
async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Triggering Litestar app…')
    # Convert req to ASGI-like call

    body = req.get_body()
    scope = {
        "type": "http",
        "method": req.method,
        "path": "/" + req.route_params.get("path", ""),
        "query_string": req.url.split("?")[1].encode() if "?" in req.url else b"",
        "headers": [(k.encode(), v.encode()) for k, v in req.headers.items()],
    }

    logging.info(f"Scope: {scope}")

    response_body = b""
    status = 500
    headers = []

    logging.info("Preparing ASGI receive")
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}
    
    logging.info("Preparing ASGI send")
    async def send(message):
        nonlocal response_body, status, headers
        if message["type"] == "http.response.start":
            status = message["status"]
            headers = message.get("headers", [])
        elif message["type"] == "http.response.body":
            response_body += message.get("body", b"")

    logging.info("Calling Litestar app…")   
    logging.info(f"[DEBUG] SCOPE PATH RECEIVED BY LITESTAR: {scope['path']}")

    await litapp(scope, receive, send)

    logging.info(f"Raw headers from ASGI app: {headers}")
    return func.HttpResponse(
    body=response_body,
    status_code=status,
    headers={k.decode() if isinstance(k, bytes) else k:
             v.decode() if isinstance(v, bytes) else v
             for k, v in headers},
    mimetype="application/json"
)

