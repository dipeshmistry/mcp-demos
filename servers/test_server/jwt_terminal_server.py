from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
import datetime
from fastmcp import FastMCP

# ---- JWT Setup ----
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

def create_token(username: str, tools: list):
    print(username)
    print(tools)
    payload = {
        "sub": username,
        "tools": tools,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    print(payload)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Create FastAPI app
app = FastAPI()

@app.post("/create_token", response_model=TokenResponse)
def api_create_token(auth: AuthRequest):
    user = USERS.get(auth.username)
    print(user)
    if not user or user["password"] != auth.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(auth.username, user["tools"])
    return TokenResponse(token=token)

# --- MCP server ---
mcp = FastMCP("TerminalServer")

@mcp.tool()
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

# Mount MCP's ASGI app under /mcp
app.mount("/mcp", mcp)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
