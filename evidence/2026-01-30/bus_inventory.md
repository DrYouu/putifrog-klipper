# Inventario de Buses e Interconexión
## Evidencia: 2026-01-30

### Comando 1: Dispositivos I2C y SPI

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /dev/i2c-* /dev/spidev* 2>/dev/null || true'
```

#### Output
```
crw-rw---- 1 root i2c 89, 0 Jan 27 23:59 /dev/i2c-0
crw-rw---- 1 root i2c 89, 1 Jan 27 23:59 /dev/i2c-1
crw-rw---- 1 root i2c 89, 2 Jan 27 23:59 /dev/i2c-2
```

#### Interpretación
- **3 buses I2C disponibles** (i2c-0, i2c-1, i2c-2)
- **Sin dispositivos SPI** (`/dev/spidev*` no existen)
- Permisos: root:i2c, accesible para usuarios en grupo `i2c`

---

### Comando 2: Dispositivos en Bus I2C (sysfs)

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /sys/bus/i2c/devices 2>/dev/null | sed -n "1,220p" || true'
```

#### Output
```
total 0
lrwxrwxrwx 1 root root 0 Jan 30 17:52 i2c-0 -> ../../../devices/platform/soc/1c2ac00.i2c/i2c-0
lrwxrwxrwx 1 root root 0 Jan 30 17:52 i2c-1 -> ../../../devices/platform/soc/1c2b000.i2c/i2c-1
lrwxrwxrwx 1 root root 0 Jan 30 17:52 i2c-2 -> ../../../devices/platform/soc/1c2b400.i2c/i2c-2
```

#### Interpretación

**Mapeo de Buses I2C a Hardware:**

| Bus | Dirección SoC | Controlador | Ruta |
|-----|---------------|-------------|------|
| i2c-0 | 0x1c2ac00 | I2C0 A13 | /sys/devices/platform/soc/1c2ac00.i2c/i2c-0 |
| i2c-1 | 0x1c2b000 | I2C1 A13 | /sys/devices/platform/soc/1c2b000.i2c/i2c-1 |
| i2c-2 | 0x1c2b400 | I2C2 A13 | /sys/devices/platform/soc/1c2b400.i2c/i2c-2 |

**No se detectan dispositivos I2C en esta consulta:**
- Posibles razones:
  1. Dispositivos no cargados/enumerados todavía
  2. Direcciones I2C no respondiendo
  3. Drivers específicos de periféricos no cargados
  4. Placa de motor está en puerto USB (no I2C)

---

### Comando 3: Dispositivos SPI (sysfs)

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /sys/bus/spi/devices 2>/dev/null | sed -n "1,220p" || true'
```

#### Output
```
total 0
```

#### Interpretación
- **SPI no está en uso** en esta configuración
- No hay dispositivos SPI detectados
- Controladores SPI pueden estar compilados en kernel pero sin periféricos

---

### Comando 4: Módulos Cargados

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'lsmod | sed -n "1,240p"'
```

#### Output
```
Module                  Size  Used by
rfkill                 20480  1
cdc_ether              16384  0
usbnet                 28672  1 cdc_ether
sun4i_codec            40960  3
sun4i_ss               28672  0
libdes                 28672  1 sun4i_ss
sunxi_cedrus           36864  0
v4l2_mem2mem           24576  1 sunxi_cedrus
videobuf2_dma_contig    20480  1 sunxi_cedrus
videobuf2_memops       16384  1 videobuf2_dma_contig
videobuf2_v4l2         24576  2 sunxi_cedrus,v4l2_mem2mem
videobuf2_common       49152  3 sunxi_cedrus,v4l2_mem2mem,videobuf2_v4l2
videodev              196608  4 sunxi_cedrus,videobuf2_common,v4l2_mem2mem,videobuf2_v4l2
mc                     32768  5 sunxi_cedrus,videobuf2_common,videodev,v4l2_mem2mem,videobuf2_v4l2
uio_pdrv_genirq        16384  0
uio                    20480  1 uio_pdrv_genirq
cpufreq_dt             16384  0
evdev                  24576  1
sun4i_ts               16384  0
hwmon                  24576  1 sun4i_ts
usb_f_acm              16384  1
u_serial               20480  3 usb_f_acm
g_serial               16384  0
libcomposite           45056  2 g_serial,usb_f_acm
fuse                  118784  3
ip_tables              28672  0
x_tables               24576  1 ip_tables
pwm_sun4i              16384  1
pwm_bl                 16384  0
panel_simple           73728  0
```

#### Interpretación

**Módulos Relevantes para Buses/Interconexión:**

| Módulo | Tamaño | Propósito | Estado |
|--------|--------|-----------|--------|
| **cdc_ether** | 16KB | Ethernet sobre USB CDC | Cargado (usado por usbnet) |
| **usbnet** | 28KB | Controlador USB networking | Cargado (1 usuario: cdc_ether) |
| **g_serial** | 16KB | USB Gadget Serial | Cargado, no usado por otros |
| **usb_f_acm** | 16KB | Función USB ACM | Cargado (1 usuario: u_serial) |
| **u_serial** | 20KB | Capa serie USB | Cargado (3 usuarios: usb_f_acm, g_serial...) |
| **libcomposite** | 45KB | Framework USB Gadget | Cargado (2 usuarios: g_serial, usb_f_acm) |

**Módulos Multimedia/Video:**
- `sunxi_cedrus` - Decodificador de video Allwinner (no vinculado a motor)
- `sun4i_codec` - Codec de audio (no vinculado a motor)
- `videodev`, `v4l2_mem2mem` - Infraestructura V4L2
- `pwm_sun4i`, `pwm_bl` - PWM para backlight (no activo)

**Módulos de Entrada:**
- `sun4i_ts` - Pantalla táctil (no presente)
- `evdev` - Eventos de entrada

**Módulos de Red:**
- `cdc_ether` → **Importante**: Ethernet sobre USB CDC (probablemente interfaz con motor)

---

### Comando 5: Mensajes de Kernel sobre Buses

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dmesg -T | grep -Ei "i2c|spi|w1|gpio|pwm|adc" || true'
```

#### Output
```
[Fri Jan 30 16:52:08 2026] sun4i-usb-phy 1c13400.phy: Couldn't request ID GPIO
[Fri Jan 30 16:52:08 2026] i2c /dev entries driver
[Fri Jan 30 16:52:08 2026] sunxi-mmc 1c0f000.mmc: Got CD GPIO
[Fri Jan 30 16:52:10 2026] pwm-backlight backlight: supply power not found, using dummy regulator
[Fri Jan 30 16:52:10 2026] pwm-backlight backlight: supply power not found, using dummy regulator
```

#### Interpretación

- **i2c /dev entries driver**: Driver I2C cargado y disponible
- **GPIO**: Presentes en el hardware (usados por MMC CD, USB PHY)
- **PWM**: Cargado para backlight LCD (sin regulador, usando dummy)
- Sin mensajes de error críticos en I2C/SPI

---

### Comando 6: Dispositivos USB (lsusb)

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'lsusb 2>/dev/null || echo "NO_LSUSB"'
```

#### Output
```
Bus 002 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 001 Device 003: ID 2357:0602 TP-Link USB 10/100 LAN
Bus 001 Device 002: ID 0424:2513 Microchip Technology, Inc. (formerly SMSC) 2.0 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

#### Interpretación

**Topología USB:**

```
Bus 1 (EHCI Host Controller)
├─ Device 001: Linux Foundation 2.0 root hub
├─ Device 002: Microchip SMSC 2.0 Hub (hub externo)
│   └─ Device 003: TP-Link USB 10/100 LAN (0x2357:0602)
│       └─ Serial: 788CB533A81D
└─ (posible Device 004+: Placa de motor? - No visible en este output)

Bus 2 (OHCI Host Controller 1.1)
└─ Device 001: Linux Foundation 1.1 root hub

Bus 3 (MUSB Host Controller)
└─ Device 001: Linux Foundation 2.0 root hub (vacío)
```

**Dispositivos Identificados:**
1. **TP-Link USB 10/100 LAN** (idVendor=2357, idProduct=0602)
   - Dirección: Bus 1, Device 3
   - Interfaz: CDC Ethernet (visto en módulos: `cdc_ether` cargado)
   - Serial: 788CB533A81D
   - Propósito: **Ethernet de red**

2. **Microchip SMSC Hub** (idVendor=0424, idProduct=2513)
   - Dirección: Bus 1, Device 2
   - Propósito: Hub externo para expandir puertos USB

**Puertos USB 3:**
- Bus 3 (MUSB): Vacío → Posible conexión futura de placa motor

---

### Comando 7: Búsqueda de Drivers USB-Serial en dmesg

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dmesg -T | grep -Ei "usb|cdc_acm|ftdi|cp210|pl2303" || true'
```

#### Output
```
(ver anterior en Comando 5 de tty_inventory.md)
[Fri Jan 30 16:52:18 2026] g_serial gadget: Gadget Serial v2.4
[Fri Jan 30 16:52:18 2026] g_serial gadget: g_serial ready
[Fri Jan 30 16:52:26 2026] cdc_ether 1-1.2:2.0 eth0: register 'cdc_ether' at usb-1c14000.usb-1.2, CDC Ethernet Device, 78:8c:b5:33:a8:1d
[Fri Jan 30 16:52:26 2026] usbcore: registered new interface driver cdc_ether
```

#### Interpretación

- **g_serial gadget**: A13 actúa como dispositivo serial USB (Device Mode)
- **cdc_ether**: Provee interfaz Ethernet sobre USB al adaptador TP-Link
- **NO hay drivers ftdi, pl2303, cp210x**: No hay convertidores USB-UART tradicionales

---

## Hipótesis sobre Interconexión con Placa de Motor

Basado en la evidencia:

1. **Puerto USB Gadget (ttyGS0)**: Active, listening
2. **CDC Ethernet**: Cargado para TP-Link LAN
3. **I2C 0-2**: Presente en hardware, buses libres
4. **UART1-3**: Disponibles en device tree pero no activos
5. **SPI**: No activo

**Escenarios posibles:**

### Escenario A: Motor comunica vía USB Device Mode (ttyGS0)
- A13 expone `/dev/ttyGS0` como puerto serie
- Placa motor se conecta vía conector USB
- Comunicación bidireccional simétrica

### Escenario B: Motor comunica vía I2C
- Placa motor habla I2C (i2c-0, i2c-1, o i2c-2)
- Driver específico pendiente de detección
- Requiere ejecutar `i2cdetect` para mapear direcciones

### Escenario C: Motor comunica vía UART (UART2 o UART3)
- Conexión serie directa (RX/TX)
- Pines físicos en módulo A13
- Requiere verificación de pinout y mapeo de `/dev/ttyS*`

---

## Conclusión

Los buses **I2C y USB Gadget** están presentes y activos.
**UART1-3** están en device tree pero esperando confirmación de uso físico.
**SPI no está activo**.

El método de comunicación más probable es **USB Gadget Serial (ttyGS0)** basado en:
- Módulo `g_serial` cargado y listo
- Port `ttyGS0` con getty activo
- Módulos USB gadget framework en uso
