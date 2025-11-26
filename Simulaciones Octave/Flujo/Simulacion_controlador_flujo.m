clear; clc;

Ts = 0.005;

a = 0.996155;
b = 0.009062;

Kp    = 2.41;
KiTs  = 0.0724;
Kd    = -0.0124;

Kd_Ts = Kd / Ts;

r0 = Kp + KiTs + Kd_Ts;
r1 = -Kp - 2*Kd_Ts;
r2 = Kd_Ts;

printf("r0 = %.6f\n", r0);
printf("r1 = %.6f\n", r1);
printf("r2 = %.6f\n\n", r2);

Tsim = 10;
N = round(Tsim / Ts);
t = (0:N-1)*Ts;

r = ones(1, N);

y = zeros(1, N);
u = zeros(1, N);
e = zeros(1, N);

for k = 3:N
  e(k) = r(k) - y(k-1);

  du   = r0*e(k) + r1*e(k-1) + r2*e(k-2);
  u(k) = u(k-1) + du;


  y(k) = a*y(k-1) + b*u(k-1);
endfor


figure(1); clf;
plot(t, r, "k--", "linewidth", 1); hold on;
plot(t, y, "b", "linewidth", 1.5);
grid on;
xlabel("Tiempo [s]");
ylabel("Salida");
title("Respuesta al escalón - Planta + PID");
legend("Referencia", "Salida");

figure(2); clf;
plot(t, u, "r", "linewidth", 1.5);
grid on;
xlabel("Tiempo [s]");
ylabel("u[k]");
title("Señal de control u[k]");

