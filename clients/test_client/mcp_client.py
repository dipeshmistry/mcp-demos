# fastmcp_client.py
from fastmcp import Client
import asyncio

async def main():
    # Pass the HTTP MCP endpoint URL
    client = Client("http://localhost:8765/mcp")

    async with client:
        tools = await client.list_tools()
        print("Available tools:", tools)

        hello = await client.call_tool("say_hello", {"name":"Dipesh"})
        print("say_hello result:", hello.content[0].text)

        summ = await client.call_tool("add", {"a":7, "b":5})
        print("add result:", summ.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
