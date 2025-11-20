from time import sleep_ms
import LeerSpO2
from machine import Pin, PWM


r = 88          
Kp = 1.0          
Ki = 0.1          
Ts = 0.020        
KI_TS = Ki * Ts   

e1 = 0.0          
u1 = 0.0          

pwm = PWM(Pin(23), freq=1000, duty_u16=0)

def aplicar_pwm(u):
    if u < 0:
        u = 0
    if u > 100:
        u = 100

    duty = int(u * 65535 / 100)
    pwm.duty_u16(duty)
    return u

if not LeerSpO2.config_spo2():
    print("Error: sensor no funciona")
else:
    print("Sensor configurado correctamente")

    while True:
        spo2 = LeerSpO2.leer_spo2()

        if isinstance(spo2, str):
            print(spo2)
            break

        if spo2 is not None:
            e0 = r - spo2   
            u0 = u1 + Kp * e0 + KI_TS * e1
            
            if u0 < 0:
                u0 = 0
            if u0 > 100:
                u0 = 100

            duty = int(u0 * 65535 / 100)
            pwm.duty_u16(duty)

            u1 = u0
            e1 = e0

            print("SpO2: {:.1f}% | Error: {:.1f}% | PWM: {:.1f}%"
                  .format(spo2, e0, u0))

        sleep_ms(20)
