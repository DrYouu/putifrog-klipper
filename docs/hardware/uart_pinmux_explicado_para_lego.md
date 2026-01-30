# UART y Pinmux en Olimex A13 — Explicado para Lego 🧱

**Fecha**: 2026-01-30  
**Público**: personas sin experiencia en Device Tree, pines, o hardware.

---

## La historia simple: dos cerebros que quieren hablar

Imagina que tienes:
- **Cerebro A**: la Olimex A13 (impresora).
- **Cerebro B**: la placa de control (que mueve los motores).

Para que hablen, necesitan:
1. Un **cable serie** (3 hilos: TX, RX, GND).
2. Que ambos cerebros tengan el mismo **idioma de velocidad** (115200 baud = 115200 palabras/segundo).
3. Que ambos cerebros tengan un **puerto serie abierto** (encendido y escuchando).

---

## ¿Por qué puede fallar aunque todo esté enchufado?

Analógicamente:
- El cable está conectado ✅
- La velocidad es correcta ✅
- Pero el **puerto no funciona** ❌

**¿Por qué?** Porque los pines de la Olimex son "multiuso":
- El pin 8 podría ser: "puerto serie TX", "GPIO digital", "PWM", "I2C", etc.
- El sistema (Linux) necesita estar **configurado para elegir** cuál de esas opciones usar.
- Eso se llama **"pinmux"** o "multiplexión de pines".

**Analogía de Lego**:
- Tienes un conectador Lego con 4 agujeros.
- Cada agujero puede conectar: una pieza estándar, una pieza articulada, un sensor, o un motor.
- Si dices "conecta el motor aquí" (pinmux UART), el agujero entiende que ese puerto espera una señal de velocidad.
- Si dices "conecta un GPIO aquí" (pinmux GPIO), el agujero entiende que es simplemente "encendido/apagado".

Si no lo configuras y lo dejas al azar, no sabes qué va a pasar. **Ese es el problema**.

---

## ¿Qué hemos investigado?

### 1. ¿Existen puertos serie en `/dev`? ✅

**Resultado**: Sí.
```
/dev/ttyS0 ← consola (ocupada por Linux)
/dev/ttyS1 ← disponible
/dev/ttyS2 ← disponible (pero...)
/dev/ttyS3 ← disponible (pero...)
/dev/ttyS4 ← disponible (pero...)
/dev/ttyS5 ← disponible (pero...)
/dev/ttyS6 ← disponible (pero...)
/dev/ttyS7 ← disponible (pero...)
```

**En Lego**: "El conectador está ahí, y tiene 8 agujeros."

Pero no todos los agujeros tienen algo atrás. Explicación en punto 3.

### 2. ¿El sistema usa Device Tree o script.bin? (Cómo se configura)

**Resultado**: Device Tree (DT).

El sistema tiene un archivo de configuración llamado **"Device Tree Blob"** (DTB) que describe:
- Qué pines existen.
- Cuál es cada puerto serie.
- Si está "encendido" o "apagado".
- Cómo multiplexar cada pin (pinmux).

**En Lego**: "Hay un manual (DTB) que dice 'en esta caja, hay 4 pines para puerto serie, y este está encendido, ese apagado'."

**¿Dónde está ese manual?** Embebido en el kernel Linux, en el archivo `/boot/kernel.itb`.

### 3. ¿Cuál UART realmente está habilitado? 🔎

**Resultado crítico**:

```
UART0 (serial@1c28000) ❌ APAGADO
UART1 (serial@1c28400) ✅ ENCENDIDO  ← Este es ttyS0 (consola del sistema)
UART2 (serial@1c28800) ❌ APAGADO
UART3 (serial@1c28c00) ❌ APAGADO
```

**En Lego**:
- El DTB (manual de la caja) dice: "Solo el agujero UART1 está habilitado."
- Ese agujero está **ocupado por la consola de Linux** (ttyS0).
- Los demás 3 agujeros existen en `/dev/ttyS*`, pero **no tienen nada atrás** (no hay electrónica UART real activa).

---

## La conclusión: ¿Qué significa para Klipper?

### ✅ Lo que funciona:

1. **Linux detecta 8 puertos serie** en `/dev/ttyS0–7`.
2. **Al menos uno está realmente activo**: UART1 (ttyS0), que es la consola.
3. **El pinmux existe en el DTB** para todos los UART (definiciones de pines).

### ❌ Lo que puede no funcionar:

1. **ttyS0 (UART1) está ocupado por la consola**.
   - Si Klipper intenta abrirlo, entrará en conflicto con los mensajes del kernel.
   - Solución: redirigir la consola a otra parte o usar otro UART.

2. **ttyS2, ttyS3, ttyS4, ... (UART0, UART2, UART3)** están deshabilitados en el DTB.
   - Existen como "stubs" en `/dev/`, pero **no hay electrónica UART real atrás**.
   - Si Klipper intenta escribir/leer, probablemente se cuelgue esperando datos que nunca llegan.

### ¿Cuál puerto debería usar Klipper?

**Depende de dónde esté físicamente el cable**:

- **Si el cable está conectado a los pines físicos de UART1 (RX/TX de ese puerto)**:
  - Hay conflicto: esos pines están en la consola.
  - Solución: redirigir la consola (vía `/proc/cmdline` o `/boot/uEnv.txt`) a otro lado (ej: UART0).
  - Luego Klipper puede usar UART1.

- **Si el cable está conectado a otros pines (UART0, UART2, UART3)**:
  - Hay que **habilitarlos en el DTB**.
  - Recompilar el DTB.
  - Reboot.
  - Luego Klipper puede usarlos.

---

## ¿Qué NO hemos hecho?

- ❌ **No cambiamos nada del sistema**.
- ❌ **No habilitamos/deshabilitamos UART**.
- ❌ **No redirigimos la consola**.
- ✅ **Solo diagnosticamos**: miramos qué hay, qué está on/off, y qué falta.

---

## Los archivos de evidencia (lee esto primero)

Para los técnicos que quieren los detalles:

1. **[evidence/2026-01-30/tty_and_kernel.md](../../../evidence/2026-01-30/tty_and_kernel.md)**
   - Qué puertos existen en `/dev`.
   - Qué dice el kernel sobre UART (dmesg).
   - Análisis: ttyS0 es la consola, ttyS1–7 disponibles.

2. **[evidence/2026-01-30/boot_config_type.md](../../../evidence/2026-01-30/boot_config_type.md)**
   - Cómo se configura el sistema (Device Tree, no script.bin).
   - Dónde está el DTB (en `/boot/kernel.itb`).

3. **[evidence/2026-01-30/dt_uart_status.md](../../../evidence/2026-01-30/dt_uart_status.md)**
   - Tabla de cada UART: habilitado/deshabilitado, pinctrl, etc.
   - Conclusión: **solo UART1 está realmente activo** (como ttyS0/consola).

---

## Próximos pasos recomendados

1. **Identificar físicamente dónde está el cable** (qué pines RX/TX).
2. **Encontrar en qué UART esos pines corresponden** (UART0, UART1, UART2, UART3).
3. **Si es UART1**: redirigir consola a otro lado.
4. **Si es otro**: habilitarlo en el DTB y recompilar.
5. **Verificar** que Klipper pueda abrir el puerto y comunicarse.

Ver plan de acción en [notes/todo/enable_uart_plan.md](../../../notes/todo/enable_uart_plan.md).

---

**Fecha del diagnóstico**: 2026-01-30  
**Responsable del diagnóstico**: VSCode Agent
