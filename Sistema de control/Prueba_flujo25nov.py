from machine import Pin, PWM, ADC
import json
import math
import sys
import time
import uselect

# ----------- CONFIGURACIÓN DE LOS ADC / PWM -----------
adc_oxigeno = ADC(Pin(5))
adc_oxigeno.atten(ADC.ATTN_11DB)   # ~0–3.3 V en ESP32

PWM_PIN = 3
pwm = PWM(Pin(PWM_PIN), freq=1000, duty_u16=0)

# ----------- CONSTANTES DE CALIBRACIÓN (V -> LPM) -----------
VMAX_O2 = 1.6     # voltaje ≈ 0 psi
VMIN    = 1.26    # voltaje ≈ 50 psi

K_FLOW = 5.2698
C0     = 103.05
C1     = 73.53


def v_to_lpm(v):
    if v < VMIN:
        v = VMIN
    elif v > VMAX_O2:
        v = VMAX_O2

    inside = C0 - C1 * v
    if inside <= 0:
        return 0.0

    q = K_FLOW * math.sqrt(inside)

    if q < 0.0:
        q = 0.0
    elif q > 15.0:
        q = 15.0

    return q


# ----------- FILTRO DEL FLUJO -----------
ALPHA = 0.01
DEADBAND = 0.1
_flujo_filtrado = None


def filtrar_flujo(q):
    global _flujo_filtrado
    if _flujo_filtrado is None:
        _flujo_filtrado = q
        return _flujo_filtrado

    if abs(q - _flujo_filtrado) < DEADBAND:
        return _flujo_filtrado

    _flujo_filtrado += ALPHA * (q - _flujo_filtrado)
    return _flujo_filtrado


# ----------- CONTROLADOR -----------
u1 = 0.0
u2 = 0.0
e1 = 0.0
e2 = 0.0
e3 = 0.0
u  = 0.0

# referencia fija por ahora (LPM)
r = 2

if r >= 12:
    KP = 0.0012166
    KI_TS = 0.000122166
elif r >= 6:
    KP = 0.000666
    KI_TS = 0.000052166
else:
    KP = 0.000126
    KI_TS = 0.000032166


def Limite_control(x):
    if x < 0.0:
        return 0.0
    if x > 1:
        return 1
    return x


def sat01(x):
    return Limite_control(x)


def leer_adc_pwm_control(adc):
    global u1, u2, e1, e2, e3, u, r

    v_sum = 0.0
    y_sum = 0.0
    N = 20

    for _ in range(N):
        try:
            raw16 = adc.read_u16()
        except AttributeError:
            # por si se usa un ADC con read() de 12 bits
            raw16 = adc.read() * 16

        v = raw16 * 4.1 / 65535.0  # voltaje estimado
        y_i = v_to_lpm(v)          # flujo instantáneo [LPM]
        y_if = filtrar_flujo(y_i)

        v_sum += v
        y_sum += y_if

    v_avg = v_sum / N
    y     = y_sum / N

    # error en LPM
    e0 = r - y
    # error relativo en %
    if r != 0:
        err = e0 / r * 100.0
    else:
        err = 0.0

    # controlador PI incremental/posicional (como lo traías)
    u0 = u1 + KP * (e0) + KI_TS * e1
    u  = sat01(u0)

    pwm.duty_u16(int(u * 65535))

    # actualizar históricos
    u2, u1 = u1, u
    e3, e2, e1 = e2, e1, e0

    print_row(u, y, v_avg, err)
    time.sleep_us(5000)

    return y


# ----------- UTILIDADES DE IMPRESIÓN / PROMEDIO -----------
_header_done = False
_row_count   = 0


def print_row(u0, y_lpm, v, err):
    global _header_done, _row_count
    if not _header_done or _row_count % 25 == 0:
        # Encabezado cada 25 filas (si lo quieres visible, descomenta)
        # print(f"{'Control':>12}  {'Retro[LPM]':>12}  {'V':>8}  {'Error[%]':>9}")
        # print(f"{'-'*12}  {'-'*12}  {'-'*8}  {'-'*9}")
        _header_done = True
    print(f"{u0:12.4f}  {y_lpm:12.3f}  {v:8.4f}\t{err:8.4f}")
    _row_count += 1


def leer_promedio(func, muestras=10):
    """Promedia varias lecturas de lazo de control (si quieres suavizar aún más)."""
    return sum(func() for _ in range(muestras)) / muestras


# ----------- ENTRADA DE COMANDOS POR STDIN -----------
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
        return None
    linea = sys.stdin.readline()
    if not linea:
        return None
    linea = linea.strip()
    if linea == "":
        return None
    try:
        comando = json.loads(linea)
        return comando
    except Exception:
        return {"_error_parse": "json_invalido", "_raw": linea}


def procesar_comando(cmd):
    """
    Recibe un diccionario (cmd) y decide qué hacer.
    Regresa SIEMPRE un dict de respuesta para imprimir con json.dumps().
    """
    if cmd is None:
        return None
    if "_error_parse" in cmd:
        return {"ack": False, "error": cmd["_error_parse"], "raw": cmd.get("_raw", "")}

    # Ejemplo básico de comandos
    if cmd.get("led") == "on":
        return {"ack": True, "led": "on"}
    elif cmd.get("led") == "off":
        return {"ack": True, "led": "off"}

    # Aquí podrías agregar cosas como cambiar referencia:
    # if "ref_flujo" in cmd:
    #     global r
    #     r = float(cmd["ref_flujo"])
    #     return {"ack": True, "ref_flujo": r}

    return {"ack": False, "error": "comando_no_identificado", "cmd": cmd}


# ----------------- Programa Principal -----------------
def main():
    while True:
        # leer comando de la Raspberry / PC si llega algo
        cmd = leer_comando()
        if cmd is not None:
            resp = procesar_comando(cmd)
            if resp is not None:
                print(json.dumps(resp))

        # Ejecutar lazo de control de flujo
        _ = leer_promedio(lambda: leer_adc_pwm_control(adc_oxigeno))


if __name__ == "__main__":
    main()
