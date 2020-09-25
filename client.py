import httpx
from httpcore import ConnectError
import asyncio

async def getChunkedData(url):
    client = httpx.AsyncClient()
    try:
        async with client.stream('GET', url) as response:
            if response.status_code == 200:
                async for chunk in response.aiter_bytes():
                    print(chunk.decode().strip()+'\n-----------------')
            else:
                print("Server response: ", response.status_code)
    except ConnectError as e:
        print("Server may be down")

if __name__ == "__main__":
    url = 'http://127.0.0.1:8000/now'
    asyncio.run(getChunkedData(url))
