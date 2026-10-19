import asyncio
import os
from dotenv import load_dotenv
from fastmcp import Client
from google import genai
from google.genai import types
from httpx import HTTPTransport
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class TokenResponse(BaseModel):
    token: str

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

jwt_token = os.getenv("jwt_token")
if not jwt_token:
    raise ValueError("jwt_token not found in .env")

# Initialize Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def clean_schema(schema):
    """Remove titles from JSON schemas recursively."""
    if isinstance(schema, dict):
        schema.pop("title", None)
        for key in schema.get("properties", {}):
            schema["properties"][key] = clean_schema(schema["properties"][key])
    return schema


def convert_mcp_tools_to_gemini(mcp_tools):
    """Convert MCP tool definitions to Gemini's Tool objects."""
    gemini_tools = []
    for tool in mcp_tools:
        parameters = clean_schema(tool.inputSchema)
        function_declaration = types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=parameters
        )
        gemini_tools.append(types.Tool(function_declarations=[function_declaration]))
    return gemini_tools


async def main():
    # Connect to FastMCP server
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    transport = HTTPTransport(
        host="localhost", 
        port=8765, 
        path="/mcp",  # match your server route
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    # Pass transport to Client
    # async with Client("http://localhost:8000/mcp",headers={"Authorization": f"Bearer {jwt_token}"}) as mcp_client:
    async with Client(transport) as mcp_client:
        tools = await mcp_client.list_tools()
        print("✅ MCP Tools:", [t for t in tools])
        print("✅ MCP Tools:", [t.name for t in tools])

        # Convert tools for Gemini
        gemini_tools = convert_mcp_tools_to_gemini(tools)

        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == "quit":
                break

            # Send user input to Gemini with tool calling enabled
            user_content = types.Content(role="user", parts=[types.Part(text=user_input)])
            gemini_response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=[user_content],
                config=types.GenerateContentConfig(tools=gemini_tools),
            )

            # Process Gemini's response
            for candidate in gemini_response.candidates:
                for part in candidate.content.parts:
                    if part.function_call:
                        # Gemini is requesting a tool call
                        tool_name = part.function_call.name
                        tool_args = part.function_call.args
                        print(f"🤖 Gemini wants to call {tool_name} with {tool_args}")

                        # Call MCP tool
                        mcp_result = await mcp_client.call_tool(tool_name, tool_args)

                        # Send tool response back to Gemini for further reasoning
                        tool_response_part = types.Part(
                            function_response=types.FunctionResponse(
                                name=tool_name,
                                response={"result": mcp_result.content[0].text}
                            )
                        )
                        tool_response_content = types.Content(role="tool", parts=[tool_response_part])

                        follow_up = gemini_client.models.generate_content(
                            model="gemini-2.0-flash-001",
                            contents=[user_content, part, tool_response_content],
                            config=types.GenerateContentConfig(tools=gemini_tools),
                        )
                        print("💬", follow_up.candidates[0].content.parts[0].text)
                    elif part.text:
                        print("💬", part.text)


if __name__ == "__main__":
    asyncio.run(main())
