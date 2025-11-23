## ================================================
## Simulación planta + PID discreto
## G(z) = 0.422378 / (1 - 0.995711 z^-1)
## Ts = 2 s
## Controlador diseñado:
##   Kp  = 0.08189
##   Ki*Ts = 0.00311
##   Kd  = -0.17
## Forma incremental:
##   u[k] = u[k-1] + r0*e[k] + r1*e[k-1] + r2*e[k-2]
## ================================================

clear; clc;

## ----- Parámetros de muestreo -----
Ts = 2;              % 2 segundos

## ----- Planta discreta -----
a = 0.995711;
b = 0.422378;
% y[k] = a*y[k-1] + b*u[k-1]

## ----- Ganancias del PID (diseñadas) -----
##Kp   = 0.08189;
##KiTs = 0.00311;      % Ki*Ts
##Kd   = -0.17;
Kp   = 8.1189;
KiTs = .311;      % Ki*Ts
Kd   = -17;

Kd_Ts = Kd / Ts;     % Kd/Ts

% Coeficientes incrementales
r0 = Kp + KiTs + Kd_Ts;         % ≈ 0
r1 = -Kp - 2*Kd_Ts;             % ≈ 0.08811
r2 = Kd_Ts;                     % ≈ -0.085

printf("Coeficientes PID incremental:\n");
printf("r0 = %.6f\n", r0);
printf("r1 = %.6f\n", r1);
printf("r2 = %.6f\n\n", r2);

## ----- Configuración de simulación -----
Tsim = 1500;                    % tiempo total [s]
N    = round(Tsim / Ts);        % número de muestras
t    = (0:N-1)*Ts;

% referencia: escalón de amplitud 1
r = ones(1, N);

% Prealocación
y = zeros(1, N);    % salida
u = zeros(1, N);    % control
e = zeros(1, N);    % error

## ----- Bucle de simulación -----
for k = 3:N
  % error (usamos y[k-1])
  e(k) = r(k) - y(k-1);

  % PID incremental
  du   = r0*e(k) + r1*e(k-1) + r2*e(k-2);
  u(k) = u(k-1) + du;

  % (opcional) saturación del control, por ejemplo:
  % u(k) = min(max(u(k), 0), 1);

  % planta: y[k] = a*y[k-1] + b*u[k-1]
  y(k) = a*y(k-1) + b*u(k-1);
endfor

graphics_toolkit ("gnuplot");

## ----- Gráficas -----
figure(1); clf;
plot(t, r, "k--", "linewidth", 1.0); hold on;
plot(t, y, "b", "linewidth", 1.5);
grid on;
xlabel("Tiempo [s]");
ylabel("Salida");
title("Respuesta al escalón: planta + PID diseñado");
legend("Referencia","Salida");

figure(2); clf;
plot(t, u, "r", "linewidth", 1.5);
grid on;
xlabel("Tiempo [s]");
ylabel("u[k]");
title("Señal de control u[k]");
