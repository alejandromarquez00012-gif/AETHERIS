import serial_reader as sr
ganancias = {"kp":0,"ki":0,"kd":0}
referencias = {"flujo":0,"spo2":0}
#{"rx":"control","ganancias":{"kp":0,"ki":0,"kd":0},"referencias":{"flujo":0,"spo2":0}}
def ganancias_set(dic):
    ganancias.clear()
    ganancias.update(dic)
def referencias_set(dic):
    referencias.clear()
    referencias.update(dic)
def parametros_set(dic):
    gain = dic.get("ganancias")
    ref = dic.get("referencias")
    ganancias_set(gain)
    referencias_set(ref)
def parametros_print():
    sr.send_cmd(ganancias)
    sr.send_cmd(referencias)
