from gtts import gTTS
import time
import os
import sys
import subprocess
import argparse
from pythonosc import udp_client

OSC_SERVER = "127.0.0.1"
OSC_PORT = 9000

def osc_conf():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=9000, help="The port the OSC server is listening on")
    parser.add_argument("--count", type=int, default=1, help="Response count number")
    args = parser.parse_args()
    client = udp_client.SimpleUDPClient(args.ip, args.port)
    return client, args.count

def text_to_speech_from_file(resp_count, client, lang="fr"):
    txt_file = f"textes/ollama_responses_{resp_count}.txt"
    output_file = f"audios/response_{resp_count}.mp3"
    wav_file = f"audios/response_{resp_count}.wav"
    
    try:
        with open(txt_file, "r", encoding="utf-8") as file:
            text = file.read().strip()
        
        if not text:
            print("Le fichier est vide, rien à synthétiser.")
            return
            
        start_time = time.time()
        tts = gTTS(text=text, lang=lang)
        tts.save(output_file)
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f'Dream processed in : {elapsed_time:.2f} seconds')
        
        # Convert mp3 to wav
        subprocess.run(['ffmpeg', '-i', output_file, wav_file], check=True)
        
        # Send filename to PD
        # time.sleep(1)
        client.send_message("/filename", wav_file)
        print("\n\n---------------------------\nLe rêve devient réalité\n---------------------------")
        time.sleep(120)
        
    except FileNotFoundError:
        print(f"Erreur : Le fichier {txt_file} n'existe pas.")
    except subprocess.CalledProcessError:
        print("Erreur lors de la conversion avec ffmpeg")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    client, resp_count = osc_conf()
    text_to_speech_from_file(resp_count, client)