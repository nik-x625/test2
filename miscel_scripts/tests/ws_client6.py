import asyncio
import websockets
import json
import time
import datetime

async def hello(symb_id: int):
    async with websockets.connect("ws://127.0.0.1:8765/", timeout=10, ping_interval=None) as websocket:
        await websocket.send('{"method":"sub_to_price_info"}')
        recv_msg = await websocket.recv()
        if 1: #recv_msg == '{"message": "sub to price info"}':
            await websocket.send(json.dumps({"method":"sub_to_market","id":symb_id}))
            recv_msg = await websocket.recv()
            counter = 1 

            task = asyncio.create_task(ping(websocket))
            while True:
                msg = await websocket.recv()
                #await return_func(msg)
                print(counter, msg[:100], end='\n\n')
                counter+=1


async def ping(websocket):
    while True:
        await websocket.send('{"message":"PING"}')
        print('------ ping')
        await asyncio.sleep
        
        
asyncio.run(hello(10))        