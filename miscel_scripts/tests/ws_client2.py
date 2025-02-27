#!/usr/bin/env python

import asyncio
import websockets
import json
import time
import numpy as np
import datetime


def create_random_data(client_name, param_name, u, sigma):
    date = datetime.datetime.utcnow()
    ms = datetime.datetime.now()
    now = time.mktime(ms.timetuple())
    s = np.random.normal(u, sigma, 1)
    data = [now, client_name, param_name, s[0]]
    return data


async def data_sender(data):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        #data = write_random_data('cpe1','cpu',50,5)

        await websocket.send(json.dumps(data))
        print('# data sent was: '+str(data))

        server_resp = await websocket.recv()
        print('# response received was: '+str(server_resp))


if __name__ == "__main__":
    while (1):
        data = create_random_data('cpe1', 'param1', 50, 500)
        
        try:
            asyncio.run(data_sender(data))
        except Exception as e:
            print('# error: '+str(e))
        print()
        time.sleep(1)
    