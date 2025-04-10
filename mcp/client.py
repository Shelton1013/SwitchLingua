# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import os
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
import dotenv
dotenv.load_dotenv("../.env")
API_KEY = os.getenv("AIPROXY_API_KEY")
model = ChatOpenAI(model="gpt-4o",base_url="https://api.bianxie.ai/v1/",api_key=API_KEY)

server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["/Users/rick/2025Spring/SwitchLingua/mcp/mcp_tools.py"],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            print(agent_response)
            return agent_response

if __name__ == "__main__":
    asyncio.run(main())