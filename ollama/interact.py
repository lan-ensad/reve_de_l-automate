import requests
import json
import os
import argparse
import subprocess
from pythonosc import udp_client
import time
import re

lieux = []
main_dir = os.path.dirname(os.path.abspath(__file__))
resp_count = 0

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "MODEL_NAME_FROM_OLLAMA"
OSC_SERVER = "THIS_MACHINE_IP"
OSC_SERVER_LIEUX = "UNITY_IP_MACHINE"
OSC_PORT = 9000

# ======== CLIENT OSC 1 ========
client_lieux = udp_client.SimpleUDPClient(OSC_SERVER_LIEUX, OSC_PORT)

# ======== CLIENT OSC 2 ========
client_filename_txt = udp_client.SimpleUDPClient(OSC_SERVER, OSC_PORT)

def how_many_files(main_dir):
    """Return the number of .txt format in the root folder"""
    files = [f for f in os.listdir(main_dir+"/textes") if f.endswith('.txt')]
    return len(files)

def save_to_file(response_text, index):
    filename = "textes/ollama_response_"+str(index)+".txt"
    with open(filename, "a", encoding="utf-8") as file:
        file.write(response_text + "\n")

def save_prompt(prompt_text, index):
    filename = "textes/prompt_"+str(index)+".txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(prompt_text + "\n")

def chat_with_ollama(model="mistral"):
    global resp_count, send_response, lieux, main_dir
    while True:
        prompt = input("De quoi voulez-vous que je rêve ? >>> ")
        if not prompt:
            print("test")
            break
        data = {"model": MODEL, "prompt": prompt, "stream": True}
        response = requests.post(OLLAMA_URL, json=data, stream=True)

        response_text = ""
        resp_count = how_many_files(main_dir)+1

        save_prompt(prompt, resp_count)

        buffer = ""
        for line in response.iter_lines():
            if line:
                msg = json.loads(line.decode())
                if "response" in msg:
                    buffer += msg["response"]
                    #===== PARSE PLACE =====
                    if ";;" in buffer:
                        # Check starter ;;
                        start_idx = buffer.find(";;")
                        if start_idx != -1:
                            end_idx = buffer.find(";;", start_idx + 2)
                            if end_idx != -1:
                                # extract ;;
                                mot = buffer[start_idx + 2:end_idx]
                                if mot.strip():
                                    lieux.append(mot)
                                buffer=""
                    #===== KEEP THE REST =====
                    else:
                        print(msg["response"], end="", flush=True)
                        response_text += msg["response"]
                        # Stream the response with OSC
                        # client_lieux.send_message("/ollama_response", msg["response"])

        print("\n") # cleaner
        
        save_to_file(response_text, resp_count)
        client_lieux.send_message("/lieux", lieux) # List send and use in Unity
        client_filename_txt.send_message("/filenametxt", f"ollama_response_{resp_count}.txt")

        print(f'lieux = {lieux}\tcompteur d\'interaction= {resp_count}')
        lieux = [] # reset places
        print('\n\nRêve en cours de construction...')

        # ======== CREATE AUDIO ========
        process = subprocess.run(["python3", "convert_to_audio.py", "--count", str(resp_count)])


if __name__ == "__main__":
    chat_with_ollama()
