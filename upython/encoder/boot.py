import network
from uosc.client import Bundle, Client, create_message
import time

OSC_IP = ""
OSC_IP2 = ""
OSC_PORT = 9000
SSID = "NETWORK_SSID"
PASSWORD = "NETWORK_PASSWORD"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

count = 0
to = 5
if not wlan.isconnected():
    print(f"Try connect to SSID : {SSID}")
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        if count>=to:
            machine.reset()
        time.sleep_ms(1000)
        count +=1
        print('.', end = " ")
        print(count)
if wlan.isconnected():
    print(f">> Connected on <{SSID}> with <{network.WLAN(network.STA_IF).ifconfig()[0]}>")

client_osc = Client(OSC_IP, OSC_PORT)
client_osc2 = Client(OSC_IP2, OSC_PORT)