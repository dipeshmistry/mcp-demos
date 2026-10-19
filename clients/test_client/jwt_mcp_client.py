import asyncio
import os
from dotenv import load_dotenv

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth

# Load JWT token from .env file
load_dotenv()
jwt_token = os.getenv("JWT_TOKEN")
if not jwt_token:
    raise ValueError("JWT_TOKEN not found in .env")

# Endpoint of your MCP server
MCP_URL = "http://localhost:8000/mcp"

async def main():
    # Create transport with Bearer Authentication
    transport = StreamableHttpTransport(url=MCP_URL)
    auth = BearerAuth(jwt_token)

    # Initialize FastMCP client with transport and auth
    async with Client(transport=transport, auth=auth) as client:
        await client.connect()
        print("✨ Connected to MCP server!")

        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        if "say_hello" in [t.name for t in tools]:
            result = await client.call_tool("say_hello", {"name": "Dipesh"})
            print("say_hello response:", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
