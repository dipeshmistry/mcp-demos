FROM python:3.11-slim

# Install git so we can install MCP SDK from GitHub
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install MCP SDK from GitHub
RUN pip install --no-cache-dir git+https://github.com/modelcontextprotocol/python-sdk.git mcp[cli] fastmcp

# Copy your project files
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8765

CMD ["python", "terminal_server.py"]
