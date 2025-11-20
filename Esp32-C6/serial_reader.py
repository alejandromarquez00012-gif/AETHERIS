import sys
import json
import time
from machine import Pin
import neopixel
import uselect


np=None
recepcion = uselect.poll()
recepcion.register(sys.stdin, uselect.POLLIN)


def set_color(r, g, b):
    np[0] = (r, g, b)
    np.write()

def configRGB():
    NEO_PIN = 8          
    NUM_LEDS = 1
    np = neopixel.NeoPixel(Pin(NEO_PIN), NUM_LEDS)   



def leer_cmd():
    """
    No bloquea.
    - Si NO hay datos -> regresa None
    - Si hay datos pero no es JSON válido -> regresa {"_error_parse": "..."}
    - Si hay datos válidos -> regresa el dict decodificado
    """
    cmd = None
    evento = recepcion.poll(0)
    if not evento:
        pass

    # hay algo en stdin
    linea = sys.stdin.readline()
    if not linea:
        pass

    linea = linea.strip()
    if linea == "":
        pass

    try:
        cmd = json.loads(linea)
    except Exception:
        # devolvemos un dict especial que indica error de parseo
        cmd = {"_error_parse": "json_invalido", "_raw": linea}
    return cmd

def procesar_cmd(cmd):
    """
    Recibe un diccionario (cmd) y decide qué hacer.
    Regresa SIEMPRE un diccionario de respuesta para imprimir con json.dumps().
    """
    _cmd = None
    if cmd is None:
        pass
    # 1. primero checamos si venía roto
    if "_error_parse" in cmd:
        _cmd = {
            "ack": False,
            "error": cmd["_error_parse"],
            "raw": cmd.get("_raw", "")
        }

    # 2. ejemplo simple: control de LED

    if cmd.get("led") == "on":
#         set_color(255, 255, 255)
        _cmd = {"ack": True, "led": "on"}

    elif cmd.get("led") == "off":
#         set_color(0, 0, 0)
        _cmd = {"ack": True, "led": "off"}
    else:
        _cmd = {"ack": False, "error": "comando_no_identificado", "cmd": cmd}
    
    return _cmd

def send_cmd(cmd):
    print(json.dumps(cmd))
