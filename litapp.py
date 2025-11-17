import asyncio
from litestar import Litestar, get
from litestar.response.streaming import Stream
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from assistant import bot_request

@get("/russia")
def russia() -> dict:
    return {"message": "Hello, World! Litestar from russia"}

@get("/china")
def china() -> dict:
    return {"message": "Hello, World! Litestar from china"}

@get("/ask-agent")
async def ask_agent(input_text: str) -> dict:
    response = await bot_request(input_text)
    return {"response": response}

@get("/streaming")
async def streaming() -> Stream:

    async def event_generator():
            for i in range(10):
                yield f"data: Ping {i}\n\n"
                asyncio.sleep(1)
    return Stream(content=event_generator(), media_type="text/event-stream")

litapp = Litestar(
    route_handlers=[russia, china, ask_agent, streaming],
    openapi_config=OpenAPIConfig(
        title="Litestar Example",
        version="0.0.1",
        description="Example with Scalar Docs",
        path="/schema/openapi.json",
        render_plugins=[ScalarRenderPlugin(path="/docs")],
    ),
)