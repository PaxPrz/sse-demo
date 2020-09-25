from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
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
    return response

app = Starlette(debug=True, routes=[
    Route('/', home),
    Route('/now', timeSSE),
], middleware=[
    Middleware(CORSMiddleware, allow_origins=['*'])
])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level='debug')