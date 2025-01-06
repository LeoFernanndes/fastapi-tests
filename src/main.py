import os

import datetime
import time

import asyncio
import concurrent.futures

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel


class UserDto(BaseModel):
    id: str
    name: str
    age: int


def cpu_bound():
    return sum(i * i for i in range(10 ** 8))


def write_to_persistence():
    with open("./persistence.txt", "a") as file:
        now = datetime.datetime.now()
        file.write(f"{str(now)}\n")


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/async")
async def home() -> UserDto:
    
    loop = asyncio.get_running_loop()
    
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_bound)
        print("async")
    
    return UserDto(id="1", name="leonel", age=31)


@app.get("/sync")
async def home() -> UserDto:
    result = cpu_bound()
    print("sync")
    return UserDto(id="1", name="leonel", age=31)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
