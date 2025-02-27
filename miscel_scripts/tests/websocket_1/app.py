#!/usr/bin/env python

import asyncio
import websockets
import json


async def handler(websocket):
    for item_from_list in [100, 84, 45, 23, 654, 102, 454]:

        event = {
            "type": "field_update",
            "field": "my_dynamic_field",
            "value": item_from_list,
        }

        await websocket.send(json.dumps(event))
        await asyncio.sleep(0.8)

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
