# Análisis de Comunicación: Placa Motores ATmega → A13 Olimex
## Fecha: 2026-01-30

## Identificación del Hardware

### Placa de Motores (MCU)
- **Microcontrolador**: ATmega1280/2560 (Arduino Mega)
- **Firmware**: Marlin 2.5 (Leapfrog Creatr HS)
- **Ubicación**: Socket integrado en placa de motores
- **Configuración Esperada**: Velocidad 250000 baud

### A13 (Host)
- **Software**: Klipper + KlipperScreen + Moonraker
- **Puerto Configurado**: `/dev/serial/by-id/<your-mcu-id>` (incorrecto - placeholder)
- **Baud Rate**: 250000
- **Reinicio**: arduino

## Problema Actual

Klipper NO puede encontrar el MCU porque:
1. ✗ No busca en puerto serie interno (`/dev/ttyS*`)
2. ✗ Configuración apunta a USB externo (`/dev/serial/by-id/`) que no existe
3. ✗ El MCU está en un socket físico interno, no vía USB

## Soluciones Posibles

### **OPCIÓN 1: UART Directo (Más Probable)**

La placa de motores probablemente está conectada al A13 vía uno de estos UART:

| UART | Dirección | Device | Estado |
|------|-----------|--------|--------|
| UART0 | 0x1c28000 | /dev/ttyS1-7 (slot 8250) | ✓ Slot disponible |
| UART2 | 0x1c28800 | /dev/ttyS1-7 (slot 8250) | ✓ Slot disponible |
| UART3 | 0x1c28c00 | /dev/ttyS1-7 (slot 8250) | ✓ Slot disponible |

**Configuración Requerida en Klipper:**

```ini
[mcu]
# Cambiar esto:
# serial: /dev/serial/by-id/<your-mcu-id>

# Por uno de estos:
serial: /dev/ttyS1      # Probar primero
baud: 250000
restart_method: arduino
```

**Comando para Probar:**
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'echo "M119" | timeout 2 cat - > /dev/ttyS1 && cat /dev/ttyS1' \
  # Si recibes respuesta Marlin → puerto correcto
```

### **OPCIÓN 2: I2C (Menos Probable pero Posible)**

Si el MCU está conectado vía I2C:

```bash
# Escanear buses I2C (requiere i2c-tools)
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'i2cdetect -y 0; i2cdetect -y 1; i2cdetect -y 2'
  
# Si ves dirección I2C (ej: 0x68), sería I2C, no serie
```

**Pero:** Klipper nativo NO soporta MCU vía I2C (usaría Marlin en UART siempre).

### **OPCIÓN 3: Verificar Pinout Físico**

Necesitas:
1. Esquemático de placa de motores
2. Verificar qué pines están conectados entre:
   - MCU ATmega (TX/RX)
   - A13 (UART pines físicos)

## Pasos Recomendados (En Orden)

### 1️⃣ **Cambiar Configuración de Klipper**

Editar `/home/olimex/printer_data/config/printer.cfg`:

```ini
[mcu]
serial: /dev/ttyS1      # ← Cambiar esta línea
baud: 250000
restart_method: arduino
```

Luego reiniciar Klipper:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'systemctl restart klipper'
```

### 2️⃣ **Verificar en Logs**

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'tail -n 50 /home/olimex/printer_data/logs/klippy.log | grep -i "mcu\|serial"'
```

Si ves `mcu 'mcu': Timed out during homing` → puerto encontrado pero sin respuesta
Si ves `Unable to open serial port` → puerto incorrecto

### 3️⃣ **Probar Otros Puertos**

Si `/dev/ttyS1` no funciona:
- Probar `/dev/ttyS2`
- Probar `/dev/ttyS3`
- Probar `/dev/ttyS4`

### 4️⃣ **Verificar Velocidad Serial**

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'stty -F /dev/ttyS1 115200 -a'
```

Si 250000 no soportado → probar 115200, 19200, etc.

## Información Adicional

**Configuración Putifrog Original** está en:
- `/home/olimex/putifrog-klipper/files/putifrog.cfg`

**Extrae que:**
- Motores: X/Y = 66.67 steps/mm, Z = 960 steps/mm
- Extrusores: 2 (Dual extrusion)
- Hotend: EPCOS 100K, max 300°C
- Cama: EPCOS 100K, max 150°C, control watermark
- Velocidades: max_velocity=400, max_z_velocity=40

---

## Siguiente Acción

**Cambia la línea de serial en printer.cfg a `/dev/ttyS1` y prueba.**

¿Quieres que edite el archivo remotamente?
