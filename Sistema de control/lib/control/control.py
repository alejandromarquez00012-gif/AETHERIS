import sistema.serial_reader as sr
import math
import control._apoyo_control as ap_ct
import time
from machine import Timer

# {"rx":"control","flujo"/"spo2":{"ganancias":{"kp":0,"ki":0,"kd":0},"referencias":0}}
# {"rx":"control","flujo":{"ganancias":{"kp":0.0012166,"ki":0.000122166,"kd":0},"referencias":8}}
# {"rx":"control","spo2":{"ganancias":{"kp":6.7,"ki":0.3,"kd":-17},"referencias":8}}
ganancias = {"flujo":{"kp":0.0012166,"ki":0.000122166,"kd":0},
             "spo2":{"kp":6.7,"ki":0.3,"kd":-17}
             } 
referencias = {"flujo":15,"spo2":95}

factores = {
    "flujo": {
        "kp_med":  0.5474,
        "kp_low":  0.1036,
        "ki_med":  0.4270,
        "ki_low":  0.2633
    },
    "spo2": {
        "kp": {
            "medio": {
                "94": 0.985,
                "93": 0.985,
                "92": 0.896,
                "91": 0.701,
                "90": 0.672,
            },
            "bajo": {
                "89": 0.642,
                "88": 0.985,
                "87": 0.985,
                "86": 0.985,
            },
        },
        "ki": {
            "medio": {
                "94": 1.033,
                "93": 1.000,
                "92": 1.000,
                "91": 0.800,
                "90": 0.767,
            },
            "bajo": {
                "89": 0.767,
                "88": 0.500,
                "87": 0.567,
                "86": 0.667,
            },
        },
    },
}

ganancias_encapsuladas = {
    "flujo": {  # flujo
        "kp": {"alto": 0, "medio": None, "bajo": None},
        "ki": {"alto": 0, "medio": None, "bajo": None},
        "kd": 0.0
    },
"spo2": {  # spo2
    "kp": {"alto": 0,"medio": {"94": None,"93": None,"92": None,"91": None,"90": None},"bajo": {"89": None,"88": None,"87": None,"86": None}},
    "ki": {"alto": 0,"medio": {"94": None,"93": None,"92": None,"91": None,"90": None},"bajo": {"89": None,"88": None,"87": None,"86": None}},
    "kd": 0.0
    }
}

errores = {
        "flujo":0,
        "spo2":0
    }

# # # # #	handler rx
KP = None
KI_TS = None
KD = None

bool_control_spo2 = False
   
def parametros_set(dic):
    global referencias,KP,KI_TS,KD
    variable = None
    if "flujo" in dic:
        variable = "flujo"
        bool_control_spo2 = False
    elif "spo2" in dic:
        variable = "spo2"
        bool_control_spo2 = True
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
    elif variable =="spo2":
        KD    = ganancias_encapsuladas[variable]["kd"]
        if referencias[variable] < 86.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["bajo"]["86"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["bajo"]["86"]

        elif referencias[variable] < 87.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["bajo"]["87"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["bajo"]["87"]

        elif referencias[variable] < 88.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["bajo"]["88"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["bajo"]["88"]

        elif referencias[variable] < 89.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["bajo"]["89"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["bajo"]["89"]

        elif referencias[variable] < 90.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["medio"]["90"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["medio"]["90"]

        elif referencias[variable] < 91.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["medio"]["91"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["medio"]["91"]

        elif referencias[variable] < 92.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["medio"]["92"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["medio"]["92"]

        elif referencias[variable] < 93.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["medio"]["93"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["medio"]["93"]

        elif referencias[variable] < 94.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["medio"]["94"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["medio"]["94"]

        elif referencias[variable] < 95.5:
            KP    = ganancias_encapsuladas[variable]["kp"]["alto"]
            KI_TS = ganancias_encapsuladas[variable]["ki"]["alto"]
#     parametros_print()
    print(f"las ganancias son {KP},{KI_TS},{KD}")
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
    if var == "flujo":
        datos["kp"]["medio"] = kp_alto * fact["kp_med"]
        datos["kp"]["bajo"]  = kp_alto * fact["kp_low"]
        datos["ki"]["medio"] = ki_ts_alto * fact["ki_med"]
        datos["ki"]["bajo"]  = ki_ts_alto * fact["ki_low"]
    else:
         for nivel in ("medio", "bajo"):
            # KP por escalón
            for spo2_key, mult in fact["kp"][nivel].items():
                # solo si existe la clave en el encapsulado
                if spo2_key in datos["kp"][nivel]:
                    datos["kp"][nivel][spo2_key] = kp_alto * mult

            # KI por escalón
            for spo2_key, mult in fact["ki"][nivel].items():
                if spo2_key in datos["ki"][nivel]:
                    datos["ki"][nivel][spo2_key] = ki_ts_alto * mult
                    
def parametros_print():
    sr.send_cmd(ganancias_encapsuladas)

# # # # 	USADOS EXTERIORES
def leer_spo2():
    return ap_ct.leer_spo2()

def init_control():
    return ap_ct.config_spo2()
# # # #     apoyo

# # # #     constantes
ALPHA = 0.01       
DEADBAND = 0.1   
_flujo_filtrado = None

VMAX_O2 = 1.27
VMIN    = 1.12

K_FLOW = 2.126

C0 = 461.76
C1 = 367.65

u1_f = 0
e1_f = 0
e2_f = 0
e3_f = 0
u1_s = 0
e1_s = 0
e2_s = 0
e3_s = 0
y_if = 0
y_sum = 0
lectura = 0
Ts=2
I1 = 0
p = 33000
adc_ = 0
def control_variable(pwm,_flujo,_spo2):    

    global errores,entradas,lectura
    global u1_f,e1_f,e2_f,e3_f,u1_s,e1_s,e2_s,e3_s,y_if,y_sum,I1,p

    global adc_
    

    if not bool_control_spo2:     
        
        e0 = referencias["flujo"] - _flujo
        
        u0 = u1_f+ KP*(e0) + KI_TS*e1_f + KD*e2_f
        
        if u0 < 0.0:
            u = 0.0
        elif u0 > 1.0:
            u = 1.0
        else:
            u = u0

        pwm.duty_u16(int(u * 65535 ))
        u1_f = u
        e3_f, e2_f, e1_f = e2_f, e1_f, e0
#         p = (p+10)%65535
#         pwm.duty_u16(int(p))
        error = e0
        
    else:
        if _spo2 is None:
            salida = None
            error = None
        else:
            e0 = referencias["spo2"] - _spo2
            I=I1+e0*Ts
            D=(e0-e1_s)/Ts

            if I>100:
                    I=100
            elif I<45:
                    I=45
            u0=KP*e0+KI_TS*I+KD*D
            if u0 < 0:
                u0 = 0
            if u0 > 100:
                u0 = 100
                
            duty = int( (45 + (0.55 * u0))*655.35)
            pwm.duty_u16(duty)

            duty=duty/65535*100
            u1_s = u0
            e3_s, e2_s, e1_s = e2_s, e1_s, e0
            error = e0

    
    time.sleep_us(5000)    
    return error
def leer_flujo(adc):
        adc_read = 0
        for _ in range(50):
            adc_read += ((adc.read() * 16)**2)
        adc_prom = math.sqrt(adc_read) / 50.0 
#         v = adc_prom * 3.3 /65535.0
# #         flujo = (1500*(0.145 - v)*1.4)-9
#         flujo = (1500*(0.145 - v))
        flujo = (.13043 * (2765 - adc_prom))+2
        if flujo < 0:
            flujo = 0
        
        return flujo
# def v_to_lpm(v):
#     
#     if v < VMIN:
#         v = VMIN
#     elif v > VMAX_O2:
#         v = VMAX_O2
# 
#     raiz = C0 - C1 * v
#     if raiz <= 0:
#         print("a")
#         return 0.0
#         None
#     q = K_FLOW * math.sqrt(raiz)
# #     q = math.sqrt(461.76-367.65)
#     
# #     if q < 0.0:
# #         q = 0.0
# #     elif q > 15.0:
# #         q = 15.0
# 
#     return q
# 
# def filtrar_flujo(q):
# 
#     global _flujo_filtrado
#     if _flujo_filtrado is None:
#         _flujo_filtrado = q
#         return _flujo_filtrado
# 
#     if abs(q - _flujo_filtrado) < DEADBAND:
#         return _flujo_filtrado
# 
#     _flujo_filtrado += ALPHA * (q - _flujo_filtrado)
#     return _flujo_filtrado


