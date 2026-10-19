import os 
import subprocess
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
import uvicorn

mcp = FastMCP("terminal")
DefaultWorkspace = os.path.expanduser("D:/Projects/aiml/mcp/workspace")

@mcp.tool()
async def run_command(command: str) -> str:
    """
    Run a shell command in the specified workspace.
    
    Args:
        command (str): The shell command to run.
        workspace (str): The directory in which to run the command.
        
    Returns:
        str: The output of the command.
    """
    try:
        result = subprocess.run(command, shell=True, cwd=DefaultWorkspace, check=True, text=True, capture_output=True)
        return result.stdout or result.stderr
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"


# app = FastAPI()

# @app.get("/sse")
# async def sse(request: Request):
#     """
#     This will stream events from the MCP server over SSE.
#     """
#     async def event_stream():
#         # This is where you would connect MCP protocol to SSE
#         # For now, let's just send a test heartbeat
#         yield "event: message\ndata: connected\n\n"

#     return StreamingResponse(event_stream(), media_type="text/event-stream")


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    mcp.run(transport='stdio')
    # server = SseServerTransport(mcp)
    # server.run(host="0.0.0.0", port=5000)