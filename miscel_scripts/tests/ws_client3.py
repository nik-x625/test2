#!/usr/bin/env python

import asyncio
import websockets
import json
import time
import numpy as np
import datetime


async def create_random_data(client_name, param_name, u, sigma):
    date = datetime.datetime.utcnow()
    ms = datetime.datetime.now()
    now = time.mktime(ms.timetuple())
    s = np.random.normal(u, sigma, 1)
    data = [now, client_name, param_name, s[0]]
    return data


async def data_sender():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:

        async for i in range(1, 10):

            data = create_random_data('cpe1', 'param1', 50, 500)

            await websocket.send(json.dumps(data))
            print('# data sent was: '+str(data))

            server_resp = await websocket.recv()
            print('# response received was: '+str(server_resp))


if __name__ == "__main__":
    asyncio.run(data_sender())
