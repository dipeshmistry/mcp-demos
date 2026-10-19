import httpx
from sseclient import SSEClient
import asyncio

class MCPClient:
    def __init__(self):
        self.sse_client = None

    async def connect_to_server_http(self, url: str):
        """
        Connect to the MCP server over HTTP/SSE.
        Args:
            url (str): The base URL of the MCP server (e.g., "http://localhost:5000/sse")
        """
        print(f"Connecting to MCP server at {url} via SSE...")
        # SSEClient is blocking, so for demo purposes, run in a thread or use as is
        self.sse_client = SSEClient(url)
        print("Connected to SSE endpoint. Listening for events...")
        try:
            for event in self.sse_client:
                print(f"Event: {event.event}, Data: {event.data}")
        except KeyboardInterrupt:
            print("Disconnected from SSE endpoint.")

    async def send_command(self, api_url: str, command: str):
        """
        Send a command to the MCP server via HTTP POST.
        Args:
            api_url (str): The API endpoint to send the command to.
            command (str): The shell command to execute.
        Returns:
            str: The result from the server.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json={"command": command})
            if response.status_code == 200:
                return response.text
            else:
                return f"Error: {response.status_code} {response.text}"

if __name__ == "__main__":
    client = MCPClient()

    async def main():
        while True:
            print("\nOptions:")
            print("1. Listen to SSE events")
            print("2. Send a shell command")
            print("3. Quit")
            choice = input("Select an option (1/2/3): ").strip()
            if choice == "1":
                print("Listening to SSE events. Press Ctrl+C to stop.")
                await asyncio.to_thread(client.connect_to_server_http, "http://localhost:5000/sse")
            elif choice == "2":
                command = input("Enter shell command to run: ").strip()
                result = await client.send_command("http://localhost:5000/run_command", command)
                print(f"Result:\n{result}")
            elif choice == "3":
                print("Exiting.")
                break
            else:
                print("Invalid option. Please try again.")