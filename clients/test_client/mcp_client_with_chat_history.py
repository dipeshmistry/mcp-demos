import asyncio
import os
from dotenv import load_dotenv
from fastmcp import Client
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

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
    async with Client("http://localhost:8765/mcp") as mcp_client:
        tools = await mcp_client.list_tools()
        print("✅ MCP Tools:", [t.name for t in tools])

        # Convert tools for Gemini
        gemini_tools = convert_mcp_tools_to_gemini(tools)

        # Chat history (Gemini expects a list of Content objects)
        chat_history = []

        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == "quit":
                break

            # Add user message to history
            user_content = types.Content(role="user", parts=[types.Part(text=user_input)])
            chat_history.append(user_content)

            # Send conversation so far to Gemini
            gemini_response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=chat_history,
                config=types.GenerateContentConfig(tools=gemini_tools),
            )

            # Process Gemini's response
            for candidate in gemini_response.candidates:
                for part in candidate.content.parts:
                    if part.function_call:
                        tool_name = part.function_call.name
                        tool_args = part.function_call.args
                        print(f"🤖 Gemini wants to call {tool_name} with {tool_args}")

                        # Call MCP tool
                        mcp_result = await mcp_client.call_tool(tool_name, tool_args)

                        # Send tool response back to Gemini
                        tool_response_part = types.Part(
                            function_response=types.FunctionResponse(
                                name=tool_name,
                                response={"result": mcp_result.content[0].text}
                            )
                        )
                        tool_response_content = types.Content(role="tool", parts=[tool_response_part])
                        chat_history.append(part)  # tool call request
                        chat_history.append(tool_response_content)  # tool response

                        # Follow-up response from Gemini with new history
                        follow_up = gemini_client.models.generate_content(
                            model="gemini-2.0-flash-001",
                            contents=chat_history,
                            config=types.GenerateContentConfig(tools=gemini_tools),
                        )
                        print("💬", follow_up.candidates[0].content.parts[0].text)
                        chat_history.append(follow_up.candidates[0].content)

                    elif part.text:
                        print("💬", part.text)
                        chat_history.append(candidate.content)


if __name__ == "__main__":
    asyncio.run(main())
