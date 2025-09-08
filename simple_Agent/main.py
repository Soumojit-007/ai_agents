# from mcp.client.session import ClientSession
# from mcp.client.stdio import stdio_client, StdioServerParameters

# from langchain_mcp_adapters.tools import load_mcp_tools
# from langgraph.prebuilt import create_react_agent
# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv
# import asyncio
# import os
# import traceback


# load_dotenv()
# print("DEBUG - GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
# print("DEBUG - FIRECRAWL_API_KEY:", os.getenv("FIRECRAWL_API_KEY"))

# # ✅ Gemini Model
# model = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     temperature=0,
#     google_api_key=os.getenv("GEMINI_API_KEY")
# )

# # ✅ Firecrawl MCP Setup
# server_params = StdioServerParameters(
#     command="npx",
#     env={
#         "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")
#     },
#     args=["--yes", "firecrawl-mcp"]
# )


# async def main():
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()

#             tools = await load_mcp_tools(session)
#             print("Available tools:", [tool.name for tool in tools])
#             print("-" * 60)

#             # ✅ Pick Firecrawl search tool
#             firecrawl_tool = next((t for t in tools if "firecrawl_search" in t.name), None)

#             # ✅ React Agent
#             agent = create_react_agent(model, tools)

#             messages = [
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a helpful assistant with access to the tool 'firecrawl'. "
#                         "Whenever the user asks about a website, company, or real-time info, "
#                         "you MUST use firecrawl to fetch fresh information. "
#                         "Do NOT rely only on your own memory."
#                     )
#                 }
#             ]

#             # Chat Loop
#             while True:
#                 user_input = input("\nYou: ")
#                 if user_input.lower().strip() == "quit":
#                     print("Goodbye!")
#                     break

#                 messages.append({
#                     "role": "user",
#                     "content": user_input[:175000]
#                 })

#                 try:
#                     # ✅ Always try Firecrawl first
#                     if firecrawl_tool:
#                         try:
#                             result = await firecrawl_tool.ainvoke({"query": user_input})
#                             print("\n🔥 Firecrawl result:", result)
#                         except Exception as e:
#                             print("❌ Firecrawl search failed:", e)
#                             traceback.print_exc()

#                     # ✅ Then let agent handle conversation
#                     agent_response = await agent.ainvoke({"messages": messages})
#                     ai_message = agent_response["messages"][-1].content
#                     print("\nAgent:", ai_message)

#                 except Exception as e:
#                     print("❌ Error occurred:", e)
#                     traceback.print_exc()


# if __name__ == "__main__":
#     asyncio.run(main())









































from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import asyncio
import os
import traceback


load_dotenv()
print("DEBUG - GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
print("DEBUG - FIRECRAWL_API_KEY:", os.getenv("FIRECRAWL_API_KEY"))

# ✅ Gemini Model
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# ✅ Firecrawl MCP Setup
server_params = StdioServerParameters(
    command="npx",
    env={
        "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")
    },
    args=["--yes", "firecrawl-mcp"]
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print("Available tools:", [tool.name for tool in tools])
            print("-" * 60)

            # ✅ Pick Firecrawl search tool
            firecrawl_tool = next((t for t in tools if "firecrawl_search" in t.name), None)

            # ✅ React Agent
            agent = create_react_agent(model, tools)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant with access to the tool 'firecrawl'. "
                        "Whenever the user asks about a website, company, or real-time info, "
                        "you MUST use firecrawl to fetch fresh information. "
                        "Always ground your answers in the Firecrawl results if available."
                    )
                }
            ]

            # Chat Loop
            while True:
                user_input = input("\nYou: ")
                if user_input.lower().strip() == "quit":
                    print("Goodbye!")
                    break

                messages.append({
                    "role": "user",
                    "content": user_input[:175000]
                })

                try:
                    firecrawl_context = ""
                    # ✅ Always try Firecrawl first
                    if firecrawl_tool:
                        try:
                            result = await firecrawl_tool.ainvoke({"query": user_input})
                            print("\n🔥 Firecrawl result:", result)
                            firecrawl_context = str(result)
                        except Exception as e:
                            print("❌ Firecrawl search failed:", e)
                            traceback.print_exc()

                    # ✅ Inject Firecrawl results into agent’s context
                    if firecrawl_context:
                        messages.append({
                            "role": "system",
                            "content": f"Here is fresh info from Firecrawl:\n{firecrawl_context}"
                        })

                    # ✅ Then let agent handle conversation
                    agent_response = await agent.ainvoke({"messages": messages})
                    ai_message = agent_response["messages"][-1].content
                    print("\nAgent:", ai_message)

                except Exception as e:
                    print("❌ Error occurred:", e)
                    traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
