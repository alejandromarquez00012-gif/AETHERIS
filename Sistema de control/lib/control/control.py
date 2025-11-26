import sistema.serial_reader as sr
import math
import control._apoyo_control as ap_ct
import time
from machine import Timer

#{"rx":"control","flujo"/"spo2":{"ganancias":{"kp":0,"ki":0,"kd":0},"referencias":0}}
# {"rx":"control","flujo":{"ganancias":{"kp":0.0012166,"ki":0.000122166,"kd":0},"referencias":8}}
ganancias = {"flujo":{"kp":0.0012166,"ki":0.000122166,"kd":0},
             "spo2":{"kp":0,"ki":0,"kd":0}
             } 
referencias = {"flujo":0,"spo2":0}
factores = {
    "flujo": {   # Flujo
        "kp_med":  0.5474,
        "kp_low":  0.1036,
        "ki_med":  0.4270,
        "ki_low":  0.2633
    },
    "spo2": {   # SpO2
        "kp_med":  1.0,
        "kp_low":  1.0,
        "ki_med":  1.0,
        "ki_low":  1.0
    }
}
ganancias_encapsuladas = {
    "flujo": {  # flujo
        "kp": {"alto": 0, "medio": None, "bajo": None},
        "ki": {"alto": 0, "medio": None, "bajo": None},
        "kd": 0.0,
    },
    "spo2": {  # spo2
        "kp": {"alto": 0.0010, "medio": None, "bajo": None},
        "ki": {"alto": 0.00010, "medio": None, "bajo": None},
        "kd": 0.0,
    },
}
errores = {
        "flujo":0,
        "spo2":0
    }

# # # # #	handler rx
KP = None
KI_TS = None
KD = None


   
def parametros_set(dic):
    global referencias,KP,KI_TS,KD
    variable = None
    if "flujo" in dic:
        variable = "flujo"
    elif "spo2" in dic:
        variable = "spo2"
    ganancias[variable].clear()
    ganancias[variable].update(dic[variable]["ganancias"])
    referencias[variable] = dic[variable]["referencias"]
    calibrar_ganancias(variable)
    if variable == "flujo":
        if referencias[variable] >= 12:
            KP    = ganancias_encapsuladas[variable]["kp"]["alto"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["alto"]
        elif referencias[variable] >= 6:
            KP    = ganancias_encapsuladas[variable]["kp"]["medio"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["medio"]
        else:
            KP    = ganancias_encapsuladas[variable]["kp"]["bajo"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["bajo"]
        KD = ganancias_encapsuladas[variable]["kd"]
    else:
        None
#     parametros_print()
# # # #     handler rx
# # # #     apoyo

def calibrar_ganancias(var):
    datos = ganancias_encapsuladas[var]
    fact  = factores[var]
    
    kp_alto = ganancias[var]["kp"]
    ki_ts_alto = ganancias[var]["ki"]
    kd = ganancias[var]["kd"]
    
    datos["kp"]["alto"] = kp_alto
    datos["ki"]["alto"] = ki_ts_alto
    datos["kd"] = kd

    datos["kp"]["medio"] = kp_alto * fact["kp_med"]
    datos["kp"]["bajo"]  = kp_alto * fact["kp_low"]
    datos["ki"]["medio"] = ki_ts_alto * fact["ki_med"]
    datos["ki"]["bajo"]  = ki_ts_alto * fact["ki_low"]

def parametros_print():
#     sr.send_cmd(ganancias)
#     sr.send_cmd(referencias)
    sr.send_cmd(ganancias_encapsuladas)
# # # #     apoyo
# # # # 	USADOS EXTERIORES
def leer_spo2():
    return ap_ct.leer_spo2()
def leer_flujo():
    return 
def init_control():
    parametros_set({"rx":"control","flujo":{"ganancias":{"kp":0.00012166,"ki":0.000122166,"kd":0},"referencias":10}})
    parametros_set({"rx":"control","spo2":{"ganancias":{"kp":0.0001,"ki":0.05,"kd":0},"referencias":90}})
    #parametros_print()
    return ap_ct.config_spo2()

ALPHA = 0.01       
DEADBAND = 0.1   
_flujo_filtrado = None
# VMAX_O2 = 1.6
VMAX_O2 = 1.13
VMIN    = 1.05
# VMAX_O2 = 4.1
# VMIN    = 3.97
# VMIN    = 1.26
K_FLOW = 5.2698
C0     = 103.05
C1     = 73.53

u1 = 0
e1 = 0
e2 = 0
e3 = 0
y_if = 0
y_sum = 0
def control_variable(adc, pwm,cmd):    

    global errores,entradas
    global u1,e1,e2,e3,y_if,y_sum
#     st = control_flujo
#     if not hasattr(st, "u1"):
#         st.u1 = 0.0
#     if not hasattr(st, "e1"):
#         st.e1 = 0.0
#     if not hasattr(st, "e2"):
#         st.e2 = 0.0
#     if not hasattr(st, "e3"):
#         st.e3 = 0.0


    

    if cmd == 'f':     

        v_sum = 0.0
        for _ in range(20):
            lectura = adc.read() * 16
#             lectura = 1.6 * 16
#             lectura = 1.26 * 16
            v = lectura * 4.1 / 65535

            y_i = v_to_lpm(v)
            y_if = filtrar_flujo(y_i)

#             if v < VMIN:
#                 v_med = VMIN
#             elif v > VMAX_O2:
#                 v_med = VMAX_O2
#             else:
#                 v_med = v
# 
#             t = (v_med - VMIN) / (VMAX_O2 - VMIN)
#             y_i = 15.8 + t * (0.0 - 15.8)

#             if y_if < 0.0: y_if = 0.0
#             if y_if > 15.0: y_if = 15.0

            v_sum += v
            y_sum += y_if
        v_prom = v_sum / 20.0
        y_prom = y_sum / 20.0
        y_sum = 0
        e0 = referencias["flujo"] - y_prom
        
        u0 = u1+ KP*(e0) + KI_TS*e1 + KD*e2
#         print(f"las constantes son p = {KP}, I = {KI_TS}, D = {KD}")
    elif cmd == 's':
        None
#         u0 = st.u1 + KP*(e0 - st.e1) + KI_TS*e0 + KD_div_TS*(e0 - 2*st.e1 + st.e2)
        
    if u0 < 0.0:
        u = 0.0
    elif u0 > 1.0:
        u = 1.0
    else:
        u = u0
#     print(f"el ciclo es: {u}")
    pwm.duty_u16(int(u * 65535 * 0.9))
#     pwm.duty_u16(int(65535 * 0.0))

#     st.u1 = u
#     st.e3, st.e2, st.e1 = st.e2, st.e1, e0
    u1 = u
    e3, e2, e1 = e2, e1, e0
    time.sleep_us(5000)    
    return y_prom, e0 , u * 65535 * 0.8

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


