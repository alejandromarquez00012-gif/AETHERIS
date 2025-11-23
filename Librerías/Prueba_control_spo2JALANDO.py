from time import sleep_ms
import LeerSpO22
from machine import Pin, PWM

r = 92
kp = 6.2        
ki = .3
kd = -17
Ts = 2       
KI_TS = ki    

# q0 = kp + ki*Ts + (kd/Ts)
# q1 = -kp - 2*(kd/Ts)
# q2 = kd/Ts

I1 = 0
e1 = 0.0
e2 = 0.0
u1 = 0.0          
u0 = 0.0
pwm = PWM(Pin(23), freq=1000, duty_u16=0)

def aplicar_pwm(u):
    if u < 0:
        u = 0
    if u > 100:
        u = 100
        
    duty = int( 45 + 0.55 * u)
    pwm.duty_u16(duty)
    return u

if not LeerSpO22.config_spo2():
    print("Error: sensor no funciona")
else:
    print("Sensor configurado correctamente")

    while True:
        try:
            spo2 = LeerSpO22.leer_spo2()
        except OSError as e:
            print("Error I2C leyendo SpO2:", e)
            sleep_ms(100)
            continue                # No se rompe el ciclo

        # Si leer_spo2 regresa texto tipo "Sin dedo"
        if isinstance(spo2, str):
            print("Aviso sensor:", spo2)
            sleep_ms(100)
            continue

        if spo2 is not None:
            e0 = r - spo2   
            I=I1+e0*Ts
            D=(e0-e1)/Ts
            if I>100:
                I=100
            elif I<45:
                I=45
#             u0 = u1 + q0 * e0 + q1 * e1 + q2* e2
            u0=kp*e0+ki*I+kd*D
            if u0 < 0:
                u0 = 0
            if u0 > 100:
                u0 = 100
                
            duty = int( (45 + (0.55 * u0))*650)
            pwm.duty_u16(duty)
            duty=duty/65535*100
            u1 = u0
            e2 = e1
            e1 = e0
            err =e0/10*100
            I1=I
            print("SpO2: {:.1f}% | Error: {:.4f}% | PWM: {:.1f}% | I:{:.1f}%"
                  .format(spo2, err, duty,I))

        sleep_ms(20)
