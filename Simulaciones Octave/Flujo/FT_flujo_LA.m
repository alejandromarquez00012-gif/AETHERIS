pkg load control

num = 0.009062;
den = [1 -0.996155];

Gz = tf(num, den, 1);
r = 1;

N = 1600;
t = 0:N;
u = r * ones(size(t));

[y, ~] = lsim(Gz, u, t);

figure;
plot(t, y, 'LineWidth', 2);
grid on;
title('Respuesta al escalón de G(z)');
xlabel('k (muestras)');
ylabel('Salida y[k]');

