import serial
import json
import threading
import queue


# objeto global para RX/TX
ser = None
# Configuración por defecto
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE    = 115200

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def iniciar_lector_serial(app,var=None,
                          serial_port=SERIAL_PORT,
                           baudrate=BAUDRATE
                           ):
    """
    Inicia un hilo que lee datos JSON desde el puerto serie
    y actualiza las variables Tkinter y colas recibidas.

    Parámetros:
    """
    global ser
    def lector_serial():
        global ser
        try:
            ser = serial.Serial(serial_port, baudrate, timeout=1)
        except Exception as e:
            print(f"[ERROR] No se pudo abrir el puerto serie: {e}")
            return

        while True:
            line = ser.readline()
            if not line:
                continue
            s = line.decode("utf-8",errors="ignore").strip()
            try:
                data = json.loads(s)
            except Exception as e:
                    print("JSON ERROR:", e, "| REPR:", repr(s))
                    continue

            def _upd():
                None

            # Actualiza en el hilo del GUI
            app.after(0, _upd)

    # Hilo en modo demonio
    hilo = threading.Thread(target=lector_serial, daemon=True)
    hilo.start()

    return hilo

def enviar_comando(data: dict):
    """
    Envía un diccionario como JSON al ESP32-C6.
    Ejemplo: enviar_comando({"led":"on"})
    """
    global ser

    #print("ser =", ser)
    if ser is None or not ser.is_open:
        print("[TX] Puerto no abierto")
        return
    try:
        linea = json.dumps(data) + "\n"
        ser.write(linea.encode("utf-8"))
        ser.flush()
        print("[TX]", linea.strip())
    except Exception as e:
        print("[TX ERROR]", e)