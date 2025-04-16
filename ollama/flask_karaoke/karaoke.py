from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading
import time
import argparse

app = Flask(__name__)
socketio = SocketIO(app)
SERVER = "THIS_MACHINE_IP"
SERVER_PORT = 5000

OSC_SERVER_IP = SERVER
OSC_PORT = 9000

MAX_DIST = 1600 # INT Max distance sent by the dolly machine in mm

current_position = 0
file = ""

def load_text_file(filename):
    try:
        with open('../textes/'+str(filename), 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return "Erreur de chargement du fichier texte."

def start_osc_server():
    dispatcher = Dispatcher()
    dispatcher.map("/position", position_handler)
    dispatcher.map("/filenametxt",filename_handler )
    server = BlockingOSCUDPServer((OSC_SERVER_IP, OSC_PORT), dispatcher)
    print(f"OSC Server up {OSC_SERVER_IP}:{OSC_PORT}")
    server.serve_forever()

#=========== OSC ===========
def position_handler(address, *args):
    global current_position, file, MAX_DIST
    if args and isinstance(args[0], int):
        osc_position = args[0]
        print(f"Position reçue: {current_position}")

        text_content = load_text_file(file)
        text_length = len(text_content)
        current_position = int((osc_position / MAX_DIST) * text_length)
        if current_position > text_length:
            current_position = text_length

        if current_position > 0 and current_position < len(text_content):
            if text_content[current_position-1] == '.':
                print("Point détecté, réinitialisation du texte affiché")
                socketio.emit('position_update', {'position': current_position, 'reset_display': True})
                return

        socketio.emit('position_update', {'position': current_position})

def filename_handler(address, *args):
    global file
    if args and isinstance(args[0], str):
        file = args[0]
        print(f'New filename : {file}')
        socketio.emit('reload')

@app.route('/')
def index():
    global file
    text_content = load_text_file(file)
    return render_template('index.html', text_content=text_content, position=current_position)

#=========== URL ===========
@app.route('/get_position')
def get_position():
    global current_position, file, MAX_DIST
    text_content = load_text_file(file)
    text_length = len(text_content)
    print(text_length)
    
    if current_position > len(text_content):
        current_position = len(text_content)
    
    osc_value = int((current_position / text_length) * MAX_DIST) if text_length > 0 else 0
    displayed_text = text_content[:current_position]
    
    return jsonify({
        'position': current_position,
        'displayed_text': displayed_text
    })

if __name__ == '__main__':
    load_text_file(file)
    osc_thread = threading.Thread(target=start_osc_server)
    osc_thread.daemon = True
    osc_thread.start()
    
    socketio.run(app, host=SERVER, port=SERVER_PORT, debug=True, use_reloader=False)