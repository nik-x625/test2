import websocket
import time
import rel
import datetime
import json
import numpy as np


try:
    import thread
except ImportError:
    import _thread as thread


def create_random_data(client_name, param_name, u, sigma):
    ms = datetime.datetime.now()
    now = time.mktime(ms.timetuple())
    s = np.random.normal(u, sigma, 1)
    data = [now, client_name, param_name, s[0]]
    return data


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

    # def run(*args):
    #     for i in range(3):
    #         time.sleep(1)
    #         print('# going to send data: ',i)
    #         ws.send(json.dumps(create_random_data('cpe1', 'param1', 50, 500)))
    #     time.sleep(1)
    #     #ws.close()
    #     #print("thread terminating...")
    # _thread.start_new_thread(run, ())
if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8765/",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open
    ws.run_forever()
