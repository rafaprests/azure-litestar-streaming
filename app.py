import asyncio
from litestar import Litestar, Response, get, post
from litestar.response.streaming import Stream
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.middleware import DefineMiddleware
from litestar.status_codes import HTTP_400_BAD_REQUEST
from assistant import bot_request
from auth_middleware import User, get_current_user, createJWTToken, JWTAuthMiddleware
from litestar.di import Provide

@post("/login", tags=["Public"])
def login(username: str, email: str) -> dict:
    user = User(username=username, email=email)
    token = createJWTToken(user)

    response = Response({"message" : "Login successful"},
                        media_type="application/json")

    #set cookie with access token
    response.set_cookie(key="access_token", 
                        value=token, 
                        httponly=True,
                        secure=True,
                        samesite="Lax")

    return response

@get("/logout", tags=["Public"])
def logout() -> dict:
    response = Response({"message": "Logged out"})

    response.delete_cookie("access_token")

    return response


@get("/russia", dependencies={"user": Provide(get_current_user)}, tags=["Protected"])
def russia(user: User) -> dict:
    """A protected endpoint that requires authentication"""

    return {"message": f"Hello, {user.username}! Litestar from russia",
            "email": user.email}

@get("/china", tags=["Public"])
def china() -> dict:
    return {"message": "Hello, World! Litestar from china"}

@get("/ask-agent", tags=["Public"])
async def ask_agent(input_text: str) -> Stream:
    if not input_text:
         return Stream(content="data: Query parameter 'input_text' is missing.\n\n",
                       media_type="text/event-stream",
                       status_code=HTTP_400_BAD_REQUEST)
    return Stream(content=bot_request(input_text), 
                  media_type="text/event-stream")

@get("/streaming", tags=["Public"])
async def streaming() -> Stream:

    async def event_generator():
            for i in range(10):
                yield f"data: Ping {i}\n\n"
                asyncio.sleep(10)
    return Stream(content=event_generator(), media_type="text/event-stream")

app = Litestar(
    route_handlers=[login, logout, russia, china, ask_agent, streaming],
    middleware=[DefineMiddleware(JWTAuthMiddleware)],
    openapi_config=OpenAPIConfig(
        title="Litestar Example",
        version="0.0.1",
        description="Example with Scalar Docs",
        path="/schema/openapi.json",
        render_plugins=[ScalarRenderPlugin(path="/docs")],
    ),
)