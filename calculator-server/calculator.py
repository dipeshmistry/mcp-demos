from mcp.server.fastmcp import FastMCP

# Name your toybox
mcp = FastMCP("Calculator Server")

# Add a tool: a function LLM can call
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# Make the server start when we run the file
if __name__ == "__main__":
    mcp.run(transport="stdio")
