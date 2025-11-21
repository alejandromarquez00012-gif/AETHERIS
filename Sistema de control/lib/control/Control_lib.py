import math
import LeerSpo2

ALPHA = 0.01       
DEADBAND = 0.1   
_flujo_filtrado = None
VMAX_O2 = 1.6
VMIN    = 1.26    
K_FLOW = 5.2698
C0     = 103.05
C1     = 73.53

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
        y_if = filtrar_flujo(y_i)

        if v < VMIN:       v_med = VMIN
        elif v > VMAX_O2:  v_med = VMAX_O2
        else:              v_med = v

        t = (v_med - VMIN) / (VMAX_O2 - VMIN)
        y_i = 15.8 + t * (0.0 - 15.8)

        if y_i < 0.0:   y_i = 0.0
        if y_i > 15.0:  y_i = 15.0

        v_sum += v
        y_sum += y_i
        
    y_prom = y_sum / 20.0
    e0 = r - y_prom

    if cmd == 'f': 
        if r >=12:
            KP = 0.0012166
            KI_TS = 0.000122166
        elif r >=6:
            KP = 0.000666
            KI_TS = 0.000052166
        else:
            KP = 0.000126
            KI_TS = 0.000032166
            
        u0 = u1+ KP*(e0) + KI_TS*e1

    elif cmd == 's':
        u0 = st.u1 + KP*(e0 - st.e1) + KI_TS*e0 + KD_div_TS*(e0 - 2*st.e1 + st.e2)
        
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
