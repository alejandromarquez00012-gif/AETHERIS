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

def leer_comando():
    """
    No bloquea.
    - Si NO hay datos -> regresa None
    - Si hay datos pero no es JSON válido -> regresa {"_error_parse": "..."}
    - Si hay datos válidos -> regresa el dict decodificado
    """
    evento = recepcion.poll(0)
    if not evento:
        return None  # nada nuevo

    # hay algo en stdin
    linea = sys.stdin.readline()
    if not linea:
        return None  # línea vacía/rara, ignoramos

    linea = linea.strip()
    if linea == "":
        return None  # pura cadena vacía, ignoramos

    try:
        comando = json.loads(linea)
        return comando
    except Exception:
        # devolvemos un dict especial que indica error de parseo
        return {"_error_parse": "json_invalido", "_raw": linea}

def procesar_comando(cmd):
    """
    Recibe un diccionario (cmd) y decide qué hacer.
    Regresa SIEMPRE un diccionario de respuesta para imprimir con json.dumps().
    """
    if cmd is None:
        return None
    # 1. primero checamos si venía roto
    if "_error_parse" in cmd:
        return {
            "ack": False,
            "error": cmd["_error_parse"],
            "raw": cmd.get("_raw", "")
        }

    # 2. ejemplo simple: control de LED

    if cmd.get("led") == "on":
#         set_color(255, 255, 255)
        return {"ack": True, "led": "on"}

    elif cmd.get("led") == "off":
#         set_color(0, 0, 0)
        return {"ack": True, "led": "off"}
    return {"ack": False, "error": "comando_no_identificado", "cmd": cmd}


while True:
    cmd = leer_comando()
    cmd = procesar_comando(cmd)
    if cmd is not None:
        print(cmd)
    time.sleep(0.1)
