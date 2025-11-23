# serial_reader.py
import serial, json, threading, queue, time

ser = None
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE    = 115200

def _parse_message(s: str):
    """Devuelve (topic, payload) soportando:
       A) {"grafica": {...}}  (root única)
    """
    clave = None
    dato = None
    identificado=False
    try:
        recepcion = json.loads(s)
        identificado = True
    except Exception:
        pass
    if identificado:
        if isinstance(recepcion, dict) : #se recibe una sola clave
            clave = next(iter(recepcion)) #capturamos a traves del iterador la primer clave
            dato = recepcion[clave]

    return clave, dato


def iniciar_lector_serial(
    app,
    serial_port = SERIAL_PORT,
    baudrate = BAUDRATE,
    handlers = None,      #la clave de los handlers deben ser las que vienen del mensaje de thonny
):
    global ser
    try:
        ser = serial.Serial(serial_port, baudrate, timeout=0.2)
    except Exception as e:
        print(f"[ERROR] No se pudo abrir el puerto: {e}")
        return

    grafica_queue = {"flujo":queue.Queue(maxsize=100),
                    "spo2":queue.Queue(maxsize = 100)}


    _handlers = handlers or {}

    def _dispatch(topic, payload):
        # 1) Si hay handler, ejecútalo en el hilo de GUI
        if topic in _handlers:
            app.after(0, _handlers[topic], payload)
        # 2) Si no hay handler y hay colas, encola
        elif topic in grafica_queue:
            try:
                grafica_queue[topic].put_nowait(payload)
            except queue.Full:
                # política: descartar el más viejo
                try:
                    _ = grafica_queue[topic].get_nowait()
                    grafica_queue[topic].put_nowait(payload)
                except queue.Empty:
                    pass
        # 3) Topic desconocido
        else:
            print(f"[INFO] topic desconocido: {topic} | payload: {payload}")

    def lector():
        while True:
            try:
                raw = ser.readline()
                if not raw:
                    continue
                s = raw.decode("utf-8", errors="ignore").strip()
                if not s:
                    continue
                # print("[RAW]", s)  # Log opcional

                topic, payload = _parse_message(s)
                if not topic:
                    print("[WARN] JSON sin topic reconocido:\n", s)
                    continue

                _dispatch(topic, payload)

            except Exception as e:
                print("[SERIAL READ ERR]", e)
                time.sleep(0.05)


    hilo = threading.Thread(target=lector, daemon=True)
    hilo.start()
    return grafica_queue


def enviar_comando(tema: str, data =  None):
    global ser
    if ser is None or not ser.is_open:
        print("[TX] Puerto no abierto")
        return
    try:
        # Inserta el tema de recepción dentro del JSON
        paquete = {"rx": tema}
        if data is not None:
            paquete.update(data)

        linea = json.dumps(paquete) + "\n"
        ser.write(linea.encode("utf-8"))
        ser.flush()
        #print("[TX]", linea.strip())

    except Exception as e:
        print("[TX ERROR]", e)