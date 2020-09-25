from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from starlette.types import Send
from sse_starlette.sse import EventSourceResponse
import uvicorn
from datetime import datetime
import asyncio
from secure import SecureHeaders, SecureCookie

csp_disabled = SecureHeaders(csp="script-src 'self'; object-src 'self'")

async def home(request):
    return JSONResponse({"message":"Hello world"})

async def getNow(request):
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    return JSONResponse({"time":now})

async def getCurrentTime(count):
    for i in range(count):
        yield datetime.now().strftime("%Y/%m/%d %H:%M:%S "+str(i))
        await asyncio.sleep(2)

async def timeSSE(request):
    gen = getCurrentTime(5)
    response = EventSourceResponse(gen)
    csp_disabled.starlette(response)
    print("completedSSE")
    return response

# async def sseGenerator():
#     for i in range(5):
#         data = datetime.now().strftime("%Y/%m/%d %H:%M:%S "+i+' -- ')
#         headers = {
#             'Content-Type': 'text/event-stream',
#             'Cache-Control': 'no-cache',
#             'Connection': 'keep-alive'
#         }
#         headers['content-length'] = len(data)
#         headers['transfer-encoding'] = 'chunked'
#         data += "\n\n"
#         yield data.encode(), headers
#         await asyncio.sleep(2)

class runThisAsyncGen(Response):
    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    }

    def __init__(self, gen):
        self.gen = gen
        self.init_headers(self.headers)

    async def __call__(self, scope, receive, send):
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": self.raw_headers,
        })

        async for d in self.gen:
            chunk = d+'\n\n'
            chunk_bytes = chunk.encode('utf-8')
            await send({
                "type": "http.response.body",
                "body": chunk_bytes,
                "more_body": True
            })
        
        await send({
            "type": "http.response.body",
            "body": b"",
            "more_body": False
        })


async def getSSETime(request):
    g = getCurrentTime(5)
    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    }
    return runThisAsyncGen(g)
    # await Response(headers=headers, status_code=200)
    # async for d in g:
    #     data = d + '\n\n'
    #     headers['content-length'] = len(data)
    #     await Response(content=data.encode(), headers=headers, status_code=200)  


app = Starlette(debug=True, routes=[
    Route('/', home),
    Route('/now', timeSSE),
    Route('/sse', getSSETime),
], middleware=[
    Middleware(CORSMiddleware, allow_origins=['*'])
])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level='debug')