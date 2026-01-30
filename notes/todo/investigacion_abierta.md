# TODO - Investigación Abierta
## Sesión: 2026-01-30

## Preguntas Críticas (Responder)

### 1. ¿Cuál es el puerto exacto de comunicación con el motor?

**Descripción**: Se identificaron 3 candidatos: USB Gadget (ttyGS0), I2C, UART2/3.

**Comando para verificar USB Gadget**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'stty -F /dev/ttyGS0 -a'
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /dev/ttyGS0' &
# Luego inyectar datos desde motor
```

**Comando para verificar I2C**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'i2cdetect -y 0'
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'i2cdetect -y 1'
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'i2cdetect -y 2'
```

**Comando para verificar UART2/3**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /dev/ttyS*'
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'strace -e ioctl systemctl status serial-getty@ttyS1.service'
```

**Referencia**: `evidence/2026-01-30/bus_inventory.md`, `docs/hardware/interconnect_hypotheses.md`

---

### 2. ¿Existen periféricos I2C en los buses?

**Descripción**: Los 3 buses I2C están presentes pero sin dispositivos detectados. Necesita verificación.

**Comando**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'apt-cache policy i2c-tools && i2cdetect -y 0'
```

**Esperado**: Mapa de direcciones I2C activas (si hay periféricos)

**Referencia**: `evidence/2026-01-30/bus_inventory.md`

---

### 3. ¿UART2 y UART3 están conectados físicamente?

**Descripción**: Device tree define UART2 @ 0x1c28800 y UART3 @ 0x1c28c00, pero no aparecen en `/dev/`.

**Comando de Verificación de Device Tree**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dtc -I fs -O dts /proc/device-tree | grep -A20 "serial@1c28800"'
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dtc -I fs -O dts /proc/device-tree | grep -A20 "serial@1c28c00"'
```

**Comando para Activar (si kernel lo soporta)**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'echo "1c28800 0" | sudo tee /proc/sys/kernel/modules'
# O recompilar kernel
```

**Referencia**: `evidence/2026-01-30/device_tree_uart.md`

---

### 4. ¿Qué versión de Klipper/Firmware está corriendo?

**Descripción**: No se capturó información sobre el software de impresión/motor.

**Comando**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -la /home/*/klipper* /opt/klipper* 2>/dev/null | head -20'
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /etc/os-release && ps aux | grep -i klipper'
```

**Referencia**: N/A (nueva línea de investigación)

---

## Investigaciones Secundarias

### 5. Mapeo Exacto de Pines del Módulo A13

**Descripción**: Necesita datasheet físico o documentación del fabricante.

**Recurso**: Documentación oficial Olimex A13 SOM
- Buscar: A13 pinout diagram
- Verificar: Qué pines están expuestos en conector J4, J5, etc.

---

### 6. Protocolo de Comunicación con Placa de Motor

**Descripción**: Necesita análisis del tráfico real.

**Comando (si ttyGS0 es activo)**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'sudo cat /dev/ttyGS0 | hexdump -C' &
# Encender motor y capturar datos
```

**Referencia**: N/A (requiere ejecución con motor activo)

---

### 7. Configuración Actual de getty/serial Logins

**Descripción**: Verificar si getty está bloqueando la comunicación del motor.

**Comando**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'systemctl status serial-getty@ttyGS0.service serial-getty@ttyS0.service'
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /etc/systemd/system/serial-getty@ttyGS0.service 2>/dev/null || find /etc -name "*getty*" | head -10'
```

**Referencia**: `evidence/2026-01-30/tty_inventory.md`

---

## Documentación Faltante

### 8. Datasheet Oficial del Allwinner A13

**Requisito**: Mapeo exacto de periféricos, direcciones de memoria, pin configuration

**Fuentes Potenciales**:
- Documentación oficial Allwinner (requiere acceso)
- Documentación Olimex A13 SOM
- Kernel source linux-allwinner

---

### 9. Esquemático de la Placa Leapfrog/Creatr HS

**Requisito**: Confirmar conexión física con A13

**Información Necesaria**:
- Qué conector USB/UART/I2C conecta el motor
- Qué velocidades/protocolos se esperan
- Requerimientos de power/ground

---

### 10. Documentación de Protocolo Klipper

**Requisito**: Comprender cómo Klipper habla con motores

**Referencia**: https://www.klipper3d.org/FAQ.html (si es aplicable)

---

## Prioridad de Ejecución

1. **P0 (Crítico)**: Verificar I2C + Monitorear ttyGS0 (#1, #2)
2. **P1 (Alto)**: Verificar UART2/3 availability (#3)
3. **P2 (Medio)**: Identificar software Klipper (#4)
4. **P3 (Bajo)**: Análisis físico de pines (#5, #9)

---

## Referencias a Archivos de Evidencia

- `evidence/2026-01-30/SESSION.md` - Resumen de sesión
- `evidence/2026-01-30/system_baseline.md` - Hardware base
- `evidence/2026-01-30/tty_inventory.md` - Puertos serie
- `evidence/2026-01-30/device_tree_uart.md` - Device tree
- `evidence/2026-01-30/bus_inventory.md` - Buses I2C/SPI/USB

---

## DESCUBRIMIENTO CRÍTICO - 2026-01-30 (ACTUALIZACIÓN)

**Identificado**: MCU Marlin en socket interno, NO USB externo

**Placa de Motores**: ATmega1280/2560 (Marlin 2.5, Leapfrog Creatr HS)
**Comunicación Esperada**: UART serie @ 250000 baud (probablemente /dev/ttyS1, S2 o S3)

**Acción Inmediata**: Cambiar printer.cfg:
```
[mcu]
serial: /dev/ttyS1      # ← Probar /dev/ttyS1, S2, S3, S4
baud: 250000
restart_method: arduino
```

Ver: `evidence/2026-01-30/marlin_communication_analysis.md` para análisis completo

## Estado de Cierre

Fecha: 2026-01-30
Iniciador de investigación: Hardware-Evidence Baseline
Siguiente acción: Cambiar puerto serie en Klipper y probar
