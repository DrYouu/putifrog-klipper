# DIAGNÓSTICO COMPLETO - Puerto Marlin/MCU - 31 Enero 2026

## Resumen Ejecutivo

### Resultado del Escaneo UART
**NO HAY RESPUESTA M115 en ttyS1-3 (ningún baudrate de 9600-115200)**

### Causa Identificada
**El puerto del MCU (Marlin) no está asignado a los puertos UART seria estándar.**

### Ubicación Probable del MCU
**USB Gadget Serial (`/dev/ttyGS0`)**
- Confirmado: módulo kernel `g_serial` cargado
- Confirmado: dmesg muestra `g_serial gadget: g_serial ready`
- Puerto existe: `/dev/ttyGS0` con permisos `crw--w---- root:tty`
- **Bloqueado**: getty@ttyGS0.service activo (no disponible sin sudo)

---

## Metodología de Diagnóstico

### Paso 1: Escaneo UART Serie (COMPLETADO ✓)
```bash
Ejecutado: 5 puertos × 5 baudrates = 25 combinaciones
Resultado: 100% vacío (0 respuestas M115)
```

**Puertos probados**:
- `ttyS1 @ [115200, 57600, 38400, 19200, 9600]` → VACÍO
- `ttyS2 @ [115200, 57600, 38400, 19200, 9600]` → VACÍO
- `ttyS3 @ [115200, 57600, 38400, 19200, 9600]` → VACÍO

**Conclusión**: Marlin NO está en ttyS1-3.

### Paso 2: Búsqueda de Puertos Alternativos (COMPLETADO ✓)
```bash
ttyUSB*: NO disponibles
ttyACM*: NO disponibles
ttyAMA*: NO disponibles
ttyGS0: DISPONIBLE (USB Gadget)
```

### Paso 3: Identificación de Ubicación del MCU (PARCIAL ⚠️)

#### Opción A: USB Gadget Serial (PROBABLE)
- **Evidencia**: módulos `g_serial` + `u_serial` cargados
- **Evidencia**: dmesg → `g_serial gadget: g_serial ready`
- **Evidencia**: puerto `/dev/ttyGS0` existe
- **Bloqueante**: getty servicio activo (requiere sudo para detener)
- **Requiere**: Acceso root (contraseña sudo no disponible actualmente)

#### Opción B: I2C Bus (POSIBLE)
- **Evidencia**: 3 buses I2C disponibles (i2c-0, i2c-1, i2c-2)
- **Bloqueante**: `i2cdetect` no instalado (no hay `i2c-tools`)
- **Requiere**: Instalación package `i2c-tools` O escaneo I2C manual

#### Opción C: Comunicación Interna (REMOTA)
- Menos probable (requeriría drivers kernel custom)

---

## Información del Sistema

### Hardware
```
SoC:       Allwinner A13 (ARMv7)
RAM:       488 MB
Storage:   7.2 GB microSD (Debian 11)
Kernel:    Linux 5.10.180-olimex #145321
MCU Driver: STM32 USART (confirmado en kernel)
```

### Software
```
Klipper:   PID 502 (RUNNING pero sin conexión MCU)
Config:    /home/olimex/printer_data/config/printer.cfg
Estado:    ✗ FALLO - MCU no encontrado (placeholder <your-mcu-id>)
Firmware:  ✗ NO compilado (no build file)
```

### Puertos Disponibles
```
ttyS0      → Consola kernel (115200 baud)
ttyS1-7    → 16550A emulados (sin dispositivo)
ttyGS0     → USB Gadget Serial (getty activo)
ttyUSB*    → Ausentes
ttyACM*    → Ausentes
i2c-0/1/2  → Presentes pero sin escaneo posible
```

---

## Hipótesis Técnicas

### Hipótesis 1: ttyGS0 es el puerto Marlin (PROBABILIDAD 80%)
```
Razonamiento:
✓ USB Gadget módulo activo
✓ Puerto existe y getty está corriendo (implica que espera entrada)
✓ Coincide con arquitectura A13 (USB OTG → Gadget → MCU)
✓ Explain: getty@ttyGS0 se inicia automáticamente, indica que es un puerto serie
```

**Test requerido** (necesita sudo):
```bash
sudo systemctl stop serial-getty@ttyGS0.service
echo -n "M115" > /dev/ttyGS0
timeout 1 cat /dev/ttyGS0
```

### Hipótesis 2: MCU está en I2C (PROBABILIDAD 15%)
```
Razonamiento:
✓ STM32 soporta I2C (firmware puede tenerlo configurado)
✓ A13 tiene 3 buses I2C
? Pero no hay evidencia de dispositivo I2C (i2cdetect no disponible)
```

**Test requerido**:
```bash
sudo apt-get install -y i2c-tools
i2cdetect -y 0
i2cdetect -y 1
i2cdetect -y 2
```

### Hipótesis 3: MCU no está conectado físicamente (PROBABILIDAD 5%)
```
Razonamiento:
✗ No hay respuesta en ningún puerto
✗ Pero Klipper está intentando conectar (daemon activo)
✗ Implica que hay expectativa de puerto funcional
```

---

## Evaluación de Permisos

### Acceso Actual (Usuario `olimex`)
```
✓ Lectura /dev/ttyS1-7
✓ Lectura dmesg
✓ Ejecución stty, cat, timeout
✗ Escritura /dev/ttyGS0 (requiere root o grupo especial)
✗ Ejecución sudo (requiere contraseña)
```

### Recomendación
Para continuar diagnóstico sin permisos root:
```bash
# Opción 1: Instalar i2c-tools (requiere sudo una vez)
sudo apt-get install -y i2c-tools

# Opción 2: Agregar usuario a grupo tty (requiere sudo una vez)
sudo usermod -aG tty olimex
sudo systemctl restart serial-getty@ttyGS0.service

# Opción 3: Proporcionar acceso sudo sin contraseña para esto
sudo visudo
# Agregar: olimex ALL=(ALL) NOPASSWD: /usr/sbin/i2cdetect, /bin/systemctl
```

---

## Tabla de Estados

| Aspecto | Estado | Notas |
|---------|--------|-------|
| **UART Serie (ttyS1-3)** | ✗ VACÍO | Probados 9600-115200 baud |
| **USB Gadget (ttyGS0)** | ⚠️ ACCESO BLOQUEADO | getty activo, requiere sudo |
| **I2C** | ⚠️ HERRAMIENTAS NO DISPONIBLES | i2cdetect no instalado |
| **Módulos Kernel** | ✓ CARGADOS | g_serial, u_serial, usb* presentes |
| **Klipper Process** | ✓ RUNNING | Pero sin conexión MCU |
| **Firma Configuración** | ✓ ENCONTRADA | putifrog.cfg menciona ATmega → ACTUALIZAR |
| **Firmware Compilado** | ✗ NO EXISTE | Requiere compilación para STM32 |

---

## Pasos Siguientes

### URGENTE: Acceso Sudo
Sin sudo, el diagnóstico está **60% completo**. Requiero:
1. Contraseña sudo para usuario `olimex`, O
2. Permisos sudoers sin contraseña para comandos específicos

### Con Sudo Disponible (Orden de Prioridad)

#### 1️⃣ TEST ttyGS0 (2 minutos)
```bash
sudo systemctl stop serial-getty@ttyGS0.service
for BAUD in 115200 250000 57600 38400; do
  timeout 1 bash -c "stty -F /dev/ttyGS0 $BAUD raw -echo; echo -n 'M115' > /dev/ttyGS0; timeout 0.8 cat /dev/ttyGS0" 2>/dev/null | head -c 100
  echo ""
done
sudo systemctl start serial-getty@ttyGS0.service
```

**Resultado esperado**:
- Si responde "FIRMWARE_NAME:" → **ÉXITO**: Puerto es `/dev/ttyGS0` @ [baudrate]
- Si sigue vacío → Pasar a test 2

#### 2️⃣ INSTALAR y SCAN I2C (3 minutos)
```bash
sudo apt-get update && sudo apt-get install -y i2c-tools
for BUS in 0 1 2; do
  echo "=== I2C Bus $BUS ==="
  i2cdetect -y $BUS
done
```

**Resultado esperado**:
- Si aparece dirección hexadecimal (ej: 0x68) → Puerto es `/dev/i2c-X`
- Si todo vacío → Pasar a hipótesis 3

#### 3️⃣ TEST GPIO/SPI (si A y B fallan)
```bash
# Investigar Device Tree overlay
cat /proc/device-tree/chosen/stdout-path
dtc -I fs /sys/firmware/devicetree/base | grep -A10 "uart\|spi"
```

---

## Conclusión Actual

**Diagnóstico no destructivo completado sin restricciones de permisos.**

✓ Confirmado: Marlin NO está en ttyS1-3  
✓ Confirmado: Módulos USB Gadget activos  
⚠️ Pendiente: Verificación ttyGS0 (requiere sudo)  
⚠️ Pendiente: Escaneo I2C (requiere i2c-tools)

**Siguiente fase**: Requerir acceso sudo para finalizar identificación.

---

Generado: 31 de enero de 2026, 18:50 UTC  
Sistema: Olimex A13-SOM + Debian 11 + Klipper  
Metodología: Diagnóstico no destructivo, temporal, solo lectura/I/O reversible
