import asyncio
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import os
import re


server_params = StdioServerParameters(command="python",args=["mcp-server.py"]) 


def llm_client(message:str) -> float:
    """
        send the message to the llm and run the response
    """

    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = openai_client.chat.completions.create(
        model= "gpt-4o-mini",
        messages=[{"role":"system",
                   "content":"You are a intelifgent assistent. you will execute tasks and prompted",
                   "role":"user",
                   "content":message}],
        max_tokens=250,
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

def get_prompt_to_identify_tool_and_arguments(query, tools):
    tools_description = "\n".join(
        [
            f"- {tool.name}\nDescription: {tool.description}\nInput Schema: {json.dumps(tool.inputSchema, indent=2)}"
            for tool in tools
        ]
    )

    return (
        "You are a helpful assistant with access to these tools:\n\n"
        f"{tools_description}\n\n"
        "Choose the appropriate tool based on the user's question.\n"
        f"User's Question: {query}\n\n"
        "If no tool is needed, reply directly.\n\n"
        "IMPORTANT: When you need to use a tool, you must ONLY respond with "
        "the exact JSON object format below, nothing else:\n"
        '```\n'
        '{\n'
        '  "tool": "tool-name",\n'
        '  "arguments": {\n'
        '    "argument-name": "value"\n'
        '  }\n'
        '}\n'
        '```\n'
        "Keep all values in **string** format."
    )



def extract_json_block(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()  # fallback



async def run(query:str):
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:

            await session.initialize() 

            tools = await session.list_tools()

            # print(tools)

            prompt = get_prompt_to_identify_tool_and_arguments(query,tools.tools)

            # print(prompt)

            llm_response = llm_client(prompt)
            print("RAW LLM Response:\n", llm_response)

            try:
                json_text = extract_json_block(llm_response)
                tool_call = json.loads(json_text)
            except json.JSONDecodeError as e:
                print("❌ Failed to parse JSON:", e)
                return

            result = await session.call_tool(tool_call["tool"], tool_call["arguments"])
            print("✅ Tool Result:", result.content[0].text)

            # Parse the JSON result
            data = json.loads(result.content[0].text)
            
            # Round BMI
            rounded_bmi = round(data, 2)

            # Print the output
            print("✅ Tool Result:", rounded_bmi)



if __name__ == "__main__":
    query = "calculate bmi for a person with weigt 70kg and height 1.75m"
    asyncio.run(run(query))