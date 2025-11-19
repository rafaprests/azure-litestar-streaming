import jwt
from typing import Any
from litestar.exceptions import NotAuthorizedException, InternalServerException
from litestar import Request
from litestar.datastructures import State
from pydantic import BaseModel
from config import USER_SCOPE_KEY, SECRET_KEY, ALGORITHM

class User(BaseModel):
    username: str
    email: str

def createJWTToken(user: User) -> str:
    payload = {
        "username": user.username,
        "email": user.email
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(request: Request[Any, User, State]) -> User:
    """Dependency to retrieve the current authenticated user from the request scope"""
    user = request.scope.get(USER_SCOPE_KEY)

    if not user:
        raise NotAuthorizedException("Could not retrieve user content.")

    return user


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Apenas processa HTTP
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Só protege /russia
        if path != "/russia":
            await self.app(scope, receive, send)
            return

        # headers vem como lista de tuplas bytes -> bytes
        raw_headers = dict(scope.get("headers") or [])
        cookie_header = raw_headers.get(b"cookie", b"").decode()

        #try to get token from cookie
        token = None
        for part in cookie_header.split(";"):
            if part.strip().startswith("access_token="):
                token = part.strip().split("=", 1)[1]
                break

        if not token:
            raise NotAuthorizedException("Auth cookie is missing.")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            user = User(
                username=payload["username"],
                email=payload["email"],
            )

            # injeta o user no escopo
            scope[USER_SCOPE_KEY] = user

            await self.app(scope, receive, send)

        except jwt.InvalidTokenError:
            raise NotAuthorizedException("Invalid token.")
        except Exception as e:
            raise InternalServerException(str(e))
