#!/usr/bin/env python
import asyncio
import websockets
import json
import random

async def handler(websocket):
    while True:
        #for item_from_list in [100, 84, 45, 23, 654, 102, 454]:

        event = {
            "type": "field_update",
            "field": "my_dynamic_field",
            "value": random.randint(100,999),
        }

        await websocket.send(json.dumps(event))
        await asyncio.sleep(1)

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
