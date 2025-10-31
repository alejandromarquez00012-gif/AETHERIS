import sys
import json
import time
from machine import Pin
import neopixel
import uselect

# --- CONFIGURACIÓN DEL LED RGB ONBOARD ---
NEO_PIN = 8          # <-- cámbialo si tu LED onboard está en otro GPIO
NUM_LEDS = 1         # casi siempre es 1 en placas dev
np = neopixel.NeoPixel(Pin(NEO_PIN),1)

def set_color(r, g, b):
    np[0] = (r, g, b)
    np.write()

while True:

    linea=input()
    # 3. Intentamos interpretar esa línea como JSON
    try:
        comando = json.loads(linea)
    except Exception:
        # si mandaron basura que no es JSON, avisamos y seguimos
        print(json.dumps({"ack": False, "error": "json_invalido"}))
        continue
    if comando.get("led") == "on":
        set_color(255,255,255)
    elif comando.get("led") == "off":
        set_color(0,0,0)
    else:
        print(json.dumps({"error":"comando no identificado"}))
    # pequeño delay para no ciclar a lo loco
    time.sleep(0.05)