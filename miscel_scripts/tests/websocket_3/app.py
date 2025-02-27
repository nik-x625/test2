from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message):
    print('Received message: ' + message)
    emit('response', 'Message received!')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)