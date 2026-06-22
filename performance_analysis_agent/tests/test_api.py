import httpx
import asyncio

async def test_chat():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat/completions",
            json={
                "session_id": "test-session",
                "message": "上季度全行存款收入增加了多少？",
                "stream": False
            },
            headers={"X-Session-Id": "test-session"}  # 实际需要有效 session
        )
        print(response.json())

if __name__ == "__main__":
    asyncio.run(test_chat())