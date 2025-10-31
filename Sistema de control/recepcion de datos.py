import sys
import json
import time
from machine import Pin
import neopixel
import uselect

# --- CONFIGURACIÓN DEL LED RGB ONBOARD ---
NEO_PIN = 8          # cámbialo si tu LED onboard está en otro GPIO
NUM_LEDS = 1
np = neopixel.NeoPixel(Pin(NEO_PIN), NUM_LEDS)

def set_color(r, g, b):
    np[0] = (r, g, b)
    np.write()

# --- CONFIGURAR EL POLLER PARA ENTRADA SERIE USB ---
recepcion = uselect.poll()
recepcion.register(sys.stdin, uselect.POLLIN)

while True:
    evento = recepcion.poll(0)  # no bloqueante

    if evento:  # hay algo disponible en stdin
        linea = sys.stdin.readline()
        if not linea:
            # llegó algo raro vacío, ignoramos
            pass
        else:
            linea = linea.strip()  # <- limpiar \n, \r, espacios etc.

            if linea != "":
                try:
                    comando = json.loads(linea)
                except Exception:
                    # si mandaron basura que no es JSON, avisamos y seguimos
                    print(json.dumps({"ack": False, "error": "json_invalido"}))
            else:
                # comando sí se pudo parsear
                if comando.get("led") == "on":
                    set_color(255, 255, 255)
                    print(json.dumps({"ack": True, "led": "on"}))

                elif comando.get("led") == "off":
                    set_color(0, 0, 0)
                    print(json.dumps({"ack": True, "led": "off"}))

                else:
                    print(json.dumps({"ack": False, "error": "comando no identificado"}))

    # pequeño delay SIEMPRE, para no ciclar al 100% la CPU
    time.sleep(0.01)
