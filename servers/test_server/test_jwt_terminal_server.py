from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt, datetime, json
from jwt import ExpiredSignatureError
from jwt.exceptions import InvalidTokenError
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

SECRET_KEY = "abc@123"
ALGORITHM = "HS256"

USERS = {
    "dipesh": {"password": "pass123", "tools": ["say_hello"]},
    "admin": {"password": "admin123", "tools": ["say_hello", "add"]}
}

class AuthRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str




def create_token(username: str, tools: list[str]) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": username,
        "tools": tools,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(hours=1)).timestamp()),
        "iss": "terminal-server"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "iat", "nbf"]},
            issuer="terminal-server"
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- MCP server ---
mcp = FastMCP("TerminalServer")

@mcp.tool()
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

# Middleware with body buffering
class JWTGate(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path.startswith("/call_tool"):
            body_bytes = await request.body()
            try:
                body_data = json.loads(body_bytes.decode())
            except:
                body_data = {}

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})

        token = auth_header.split(" ", 1)[1]
        payload = verify_token(token)

        # Tool-level permission check
        if request.url.path.endswith("/call_tool"):
            tool_name = body_data.get("name")
            if tool_name not in payload.get("tools", []):
                return JSONResponse(status_code=403, content={"detail": f"Not authorized for tool '{tool_name}'"})

            # Restore body so FastMCP can still read it
            async def receive() -> Message:
                return {"type": "http.request", "body": body_bytes, "more_body": False}
            request._receive = receive

        request.scope["user"] = payload.get("sub")
        request.scope["user_tools"] = payload.get("tools", [])
        return await call_next(request)

# Main app
app = FastAPI()

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise

@app.post("/create_token", response_model=TokenResponse)
def api_create_token(auth: AuthRequest):
    user = USERS.get(auth.username)
    if not user or user["password"] != auth.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(auth.username, user["tools"])
    return TokenResponse(token=token)

# Protected MCP sub-app
mcp_asgi = getattr(mcp, "asgi_app", mcp)
mcp_protected_app = Starlette()
mcp_protected_app.mount("/", mcp_asgi)
mcp_protected_app.add_middleware(JWTGate)

# Mount MCP under /mcp
app.mount("/mcp", mcp_protected_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
