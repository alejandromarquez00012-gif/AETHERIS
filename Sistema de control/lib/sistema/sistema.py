from machine import Pin

#{"rx":"sistema"}
estado = False

def toggle_estado():
    # print("hola")
    global estado
    estado = not estado
    

