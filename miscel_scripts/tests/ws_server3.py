#!/usr/bin/env python
import asyncio
import websockets
import json
import clickhouse_connect
from datetime import datetime

client = clickhouse_connect.get_client(
    host='localhost', port='7010', username='default')

client.command('CREATE TABLE IF NOT EXISTS table1 (ts DATETIME, client_name String, param_name String, param_value Float64) ENGINE MergeTree ORDER BY client_name')


async def data_receiver(websocket):
    data = await websocket.recv()
    data = json.loads(data)
    data[0] = datetime.fromtimestamp(data[0])
    print('# data to write: '+str(data))
    client.insert('table1', [data], column_names=[
                  'ts', 'client_name', 'param_name', 'param_value'])

    confirmation = 'ok'
    await websocket.send(confirmation)
    print('# sent back the confirmation')


async def main():
    async with websockets.serve(data_receiver, "127.0.0.1", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":

    print('going to run the server main')
    asyncio.run(main())
    print('after running the main')
