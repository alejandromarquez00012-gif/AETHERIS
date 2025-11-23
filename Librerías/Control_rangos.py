import math
import LeerSpo2

ALPHA = 0.01
DEADBAND = 0.1
_flujo_filtrado = None

VMAX_O2 = 1.6
VMIN    = 1.26
K_FLOW  = 5.2698
C0      = 103.05
C1      = 73.53


_KP_F_MEDIO_FACTOR = 0.5474   
_KP_F_BAJO_FACTOR  = 0.1036   
_KI_F_MEDIO_FACTOR = 0.4270   
_KI_F_BAJO_FACTOR  = 0.2633   

_KP_S_MEDIO_FACTOR = 1.0
_KP_S_BAJO_FACTOR  = 1.0
_KI_S_MEDIO_FACTOR = 1.0
_KI_S_BAJO_FACTOR  = 1.0


KP_F_ALTO     = 0.0012166
KI_F_TS_ALTO  = 0.000122166
KP_F_MEDIO    = KP_F_ALTO    * _KP_F_MEDIO_FACTOR
KP_F_BAJO     = KP_F_ALTO    * _KP_F_BAJO_FACTOR
KI_F_TS_MEDIO = KI_F_TS_ALTO * _KI_F_MEDIO_FACTOR
KI_F_TS_BAJO  = KI_F_TS_ALTO * _KI_F_BAJO_FACTOR
KD_F          = 0.0   

KP_S_ALTO     = 0.0010
KI_S_TS_ALTO  = 0.00010
KP_S_MEDIO    = KP_S_ALTO    * _KP_S_MEDIO_FACTOR
KP_S_BAJO     = KP_S_ALTO    * _KP_S_BAJO_FACTOR
KI_S_TS_MEDIO = KI_S_TS_ALTO * _KI_S_MEDIO_FACTOR
KI_S_TS_BAJO  = KI_S_TS_ALTO * _KI_S_BAJO_FACTOR
KD_S          = 0.0   


def configurar_ganancias(cmd, kp_alto, ki_ts_alto, kd):
 
    global KP_F_ALTO, KI_F_TS_ALTO, KP_F_MEDIO, KP_F_BAJO, KI_F_TS_MEDIO, KI_F_TS_BAJO, KD_F
    global KP_S_ALTO, KI_S_TS_ALTO, KP_S_MEDIO, KP_S_BAJO, KI_S_TS_MEDIO, KI_S_TS_BAJO, KD_S

    if cmd == 'f':
        KP_F_ALTO     = kp_alto
        KI_F_TS_ALTO  = ki_ts_alto
        KD_F          = kd

        KP_F_MEDIO    = kp_alto   * _KP_F_MEDIO_FACTOR
        KP_F_BAJO     = kp_alto   * _KP_F_BAJO_FACTOR
        KI_F_TS_MEDIO = ki_ts_alto * _KI_F_MEDIO_FACTOR
        KI_F_TS_BAJO  = ki_ts_alto * _KI_F_BAJO_FACTOR

    elif cmd == 's':
        KP_S_ALTO     = kp_alto
        KI_S_TS_ALTO  = ki_ts_alto
        KD_S          = kd

        KP_S_MEDIO    = kp_alto   * _KP_S_MEDIO_FACTOR
        KP_S_BAJO     = kp_alto   * _KP_S_BAJO_FACTOR
        KI_S_TS_MEDIO = ki_ts_alto * _KI_S_MEDIO_FACTOR
        KI_S_TS_BAJO  = ki_ts_alto * _KI_S_BAJO_FACTOR


def control_flujo(adc, pwm, r, cmd):

    st = control_flujo
    if not hasattr(st, "u1"):
        st.u1 = 0.0
    if not hasattr(st, "e1"):
        st.e1 = 0.0
    if not hasattr(st, "e2"):
        st.e2 = 0.0
    if not hasattr(st, "e3"):
        st.e3 = 0.0

    v_sum = 0.0
    y_sum = 0.0
    for _ in range(20):
        lectura = adc.read() * 16
        v = lectura * 4.1 / 65535

        y_i = v_to_lpm(v)
        _ = filtrar_flujo(y_i)

        if v < VMIN:
            v_med = VMIN
        elif v > VMAX_O2:
            v_med = VMAX_O2
        else:
            v_med = v

        t = (v_med - VMIN) / (VMAX_O2 - VMIN)
        y_i = 15.8 + t * (0.0 - 15.8)

        if y_i < 0.0: y_i = 0.0
        if y_i > 15.0: y_i = 15.0

        v_sum += v
        y_sum += y_i

    y_prom = y_sum / 20.0
    e0 = r - y_prom

    if cmd == 'f':
        if r >= 12:
            KP    = KP_F_ALTO
            KI_TS = KI_F_TS_ALTO
        elif r >= 6:
            KP    = KP_F_MEDIO
            KI_TS = KI_F_TS_MEDIO
        else:
            KP    = KP_F_BAJO
            KI_TS = KI_F_TS_BAJO
        KD = KD_F

    elif cmd == 's':
        if r >= 12:
            KP    = KP_S_ALTO
            KI_TS = KI_S_TS_ALTO
        elif r >= 6:
            KP    = KP_S_MEDIO
            KI_TS = KI_S_TS_MEDIO
        else:
            KP    = KP_S_BAJO
            KI_TS = KI_S_TS_BAJO
        KD = KD_S
    else:
        KP = KI_TS = KD = 0.0

    u0 = st.u1+ KP*(e0) + KI_TS*st.e1 + KD*st.e2

    if u0 < 0.0:
        u = 0.0
    elif u0 > 1.0:
        u = 1.0
    else:
        u = u0

    pwm.duty_u16(int(u * 65535))

    st.u1 = u
    st.e3, st.e2, st.e1 = st.e2, st.e1, e0

    return y_prom


def v_to_lpm(v):
    if v < VMIN:
        v = VMIN
    elif v > VMAX_O2:
        v = VMAX_O2

    raiz = C0 - C1 * v
    if raiz <= 0:
        return 0.0

    q = K_FLOW * math.sqrt(raiz)

    if q < 0.0:
        q = 0.0
    elif q > 15.0:
        q = 15.0

    return q


def filtrar_flujo(q):
    global _flujo_filtrado
    if _flujo_filtrado is None:
        _flujo_filtrado = q
        return _flujo_filtrado

    if abs(q - _flujo_filtrado) < DEADBAND:
        return _flujo_filtrado

    _flujo_filtrado += ALPHA * (q - _flujo_filtrado)
    return _flujo_filtrado
