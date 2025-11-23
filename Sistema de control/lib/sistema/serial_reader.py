import sys
import json
import time
from machine import Pin
import uselect

recepcion = uselect.poll()
recepcion.register(sys.stdin, uselect.POLLIN)


def capturar_cmd():
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
    else:
        # hay algo en stdin
        linea = sys.stdin.readline()
        if not linea:
            pass
        else:
            linea = linea.strip()
            if linea == "":
                pass
            else:
                try:
                    cmd = json.loads(linea)
                    #print("se recibio")
                except Exception:
                    # devolvemos un dict especial que indica error de parseo
                    cmd = {"_error_parse": "json_invalido", "_raw": linea}
                    
    return cmd

def leer_cmd():
    """
    Recibe un diccionario (cmd) y decide qué hacer.
    Regresa SIEMPRE un diccionario de respuesta para imprimir con json.dumps().
    """

    _cmd = None
    
    cmd = capturar_cmd()
    
    
    if cmd is None:
        pass
    else:
        # 1. primero checamos si venía roto
        if "_error_parse" in cmd:
            _cmd = {
                "ack": False,
                "error": cmd["_error_parse"],
                "raw": cmd.get("_raw", "")
            }
            send_cmd(_cmd)
        elif "rx" in cmd:
            _cmd = cmd
        else:
            _cmd = {"ack": False, "error": "formato_dic_incorrecto", "cmd": cmd}
            send_cmd(_cmd)
            _cmd = None
    return _cmd

def send_cmd(cmd):
    print(json.dumps(cmd))
    
def send_cmd_not_id():
    print(json.dumps({"ack": False, "error": "cmd_no_identificado"}))


