import asyncio

from groq import AsyncGroq

from ghost_brain.config import get_settings


async def main():
    settings = get_settings()
    client = AsyncGroq(api_key=settings.groq_api_key)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather in Paris right now?"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "search_web",
                        "arguments": '{"query": "weather in Paris"}',
                    },
                    "type": "function",
                }
            ],
        },
        {"role": "tool", "content": "It is sunny and 25C.", "tool_call_id": "call_123"},
        {"role": "user", "content": "And what about London?"},
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
        }
    ]

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=messages, tools=tools, stream=True
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
            elif chunk.choices and chunk.choices[0].delta.tool_calls:
                print(f"Tool call: {chunk.choices[0].delta.tool_calls}")
    except Exception as e:
        print("Error:", e)


asyncio.run(main())
