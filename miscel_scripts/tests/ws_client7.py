import websocket


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



#websocket.enableTrace(True)
ws = websocket.WebSocket()
ws.connect("ws://localhost:8765")#, origin="testing_websockets.com")
while(1):
    data = create_random_data('cpe1', 'param1', 50, 500)
    ws.send(json.dumps(data))
    ws.close()
    #res = ws.recv_frame()
    
    time.sleep(1)



