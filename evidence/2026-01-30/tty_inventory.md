# Inventario de Puertos Serie (TTY)
## Evidencia: 2026-01-30

### Comando 1: Listar Dispositivos TTY Disponibles

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /dev/ttyS* /dev/ttyUSB* /dev/ttyACM* /dev/ttyAMA* 2>/dev/null || true'
```

#### Output
```
crw--w---- 1 root tty     4, 64 Jan 27 23:59 /dev/ttyS0
crw-rw---- 1 root dialout 4, 65 Jan 27 23:58 /dev/ttyS1
crw-rw---- 1 root dialout 4, 66 Jan 27 23:58 /dev/ttyS2
crw-rw---- 1 root dialout 4, 67 Jan 27 23:58 /dev/ttyS3
crw-rw---- 1 root dialout 4, 68 Jan 27 23:58 /dev/ttyS4
crw-rw---- 1 root dialout 4, 69 Jan 27 23:58 /dev/ttyS5
crw-rw---- 1 root dialout 4, 70 Jan 27 23:58 /dev/ttyS6
crw-rw---- 1 root dialout 4, 71 Jan 27 23:58 /dev/ttyS7
```

#### Interpretación
- **Dispositivos serie UART presentes**: ttyS0 a ttyS7 (8 puertos)
- **ttyS0**: Permisos diferentes (crw--w----), propiedad root:tty → **puerto de consola del sistema**
- **Otros (ttyS1-7)**: Permisos crw-rw----, propiedad root:dialout → puertos accesibles para usuario en grupo `dialout`
- **Ausentes**: ttyUSB*, ttyACM*, ttyAMA* (no hay dispositivos USB-serial conectados permanentemente)

---

### Comando 2: Directorios de Serial por ID/Path

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /dev/serial/by-id /dev/serial/by-path 2>/dev/null || true'
```

#### Output
```
(sin salida - directorios no existen o están vacíos)
```

#### Interpretación
- No hay dispositivos USB-serial enumerados en `/dev/serial/by-id` o `/dev/serial/by-path`
- Implica que no hay conversores USB-to-UART permanentes conectados

---

### Comando 3: Resolución Física de Dispositivos TTY

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'for x in /sys/class/tty/ttyS*; do echo "===$x==="; readlink -f "$x/device"; done 2>/dev/null || true'
```

#### Output
```
===/sys/class/tty/ttyS0===
/sys/devices/platform/soc/1c28400.serial
===/sys/class/tty/ttyS1===
/sys/devices/platform/serial8250
===/sys/class/tty/ttyS2===
/sys/devices/platform/serial8250
===/sys/class/tty/ttyS3===
/sys/devices/platform/serial8250
===/sys/class/tty/ttyS4===
/sys/devices/platform/serial8250
===/sys/class/tty/ttyS5===
/sys/devices/platform/serial8250
===/sys/class/tty/ttyS6===
/sys/devices/platform/serial8250
===/sys/class/tty/ttyS7===
/sys/devices/platform/serial8250
```

#### Interpretación
- **ttyS0**: Controlador nativo Allwinner @ dirección 0x1c28400 (driver dw-apb-uart)
- **ttyS1-7**: Emulados por driver genérico `serial8250` (16550A compatible)
- La dirección 0x1c28400 es el UART0 principal del Allwinner A13

---

### Comando 4: Búsqueda de TTY en dmesg

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dmesg -T | grep -Ei "ttyS|ttyAMA|ttyACM|ttyUSB|uart|serial|sunxi" || true'
```

#### Output
```
[Fri Jan 30 16:52:07 2026] Kernel command line: root=PARTUUID=023aa8cd-01 rootwait console=ttyS0,115200 panic=10 loglevel=4 
[Fri Jan 30 16:52:08 2026] sun5i-pinctrl 1c20800.pinctrl: initialized sunXi PIO driver
[Fri Jan 30 16:52:08 2026] Serial: 8250/16550 driver, 8 ports, IRQ sharing disabled
[Fri Jan 30 16:52:08 2026] printk: console [ttyS0] disabled
[Fri Jan 30 16:52:08 2026] 1c28400.serial: ttyS0 at MMIO 0x1c28400 (irq = 34, base_baud = 1500000) is a 16550A
[Fri Jan 30 16:52:08 2026] printk: console [ttyS0] enabled
[Fri Jan 30 16:52:08 2026] sunxi-wdt 1c20c90.watchdog: Watchdog enabled (timeout=16 sec, nowayout=0)
[Fri Jan 30 16:52:08 2026] sunxi-mmc 1c0f000.mmc: initialized, max. request size: 16384 KB
[Fri Jan 30 16:52:18 2026] g_serial gadget: Gadget Serial v2.4
[Fri Jan 30 16:52:18 2026] g_serial gadget: g_serial ready
```

#### Interpretación
- **Parámetro kernel**: `console=ttyS0,115200` → ttyS0 es puerto de consola del kernel, 115200 baud
- **8250 driver**: Registra 8 puertos UART compatibles con 16550
- **USB Gadget Serial**: El kernel carga `g_serial` v2.4 → **posible comunicación USB hacia placa de motor**

---

### Comando 5: Búsqueda de TTY en Journal del Kernel

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'journalctl -k --no-pager | grep -Ei "ttyS|ttyAMA|ttyACM|ttyUSB|uart|serial|sunxi" || true'
```

#### Output
```
(mismo contenido que dmesg, desde boot anterior)
```

#### Interpretación
- Journal persiste información de boot anterior
- Confirma estados de TTY desde inicio del sistema

---

### Comando 6: Parámetro Console en cmdline

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /proc/cmdline | tr " " "\n" | grep -E "^console=" || true'
```

#### Output
```
console=ttyS0,115200
```

#### Interpretación
- Console kernel: ttyS0 @ 115200 baud (confirmado)

---

### Comando 7: Servicios Serial-Getty Activos

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'systemctl list-units --type=service --all | grep -E "serial-getty@|getty@ttyS|getty@ttyAMA" || true'
```

#### Output
```
  serial-getty@ttyGS0.service                   loaded    active     running      Serial Getty on ttyGS0
  serial-getty@ttyS0.service                    loaded    active     running      Serial Getty on ttyS0
```

#### Interpretación
- **ttyS0**: Serial Getty activo → login shell disponible en puerto de consola
- **ttyGS0**: Serial Getty activo en USB gadget serial → **login disponible vía USB**
- **DESCUBRIMIENTO IMPORTANTE**: `ttyGS0` es un puerto USB gadget, probablemente conexión a placa de motor

---

## Resumen General

### Puertos Disponibles
| Puerto | Tipo | Driver | Accesible | Estado |
|--------|------|--------|-----------|--------|
| ttyS0 | UART Nativo A13 | dw-apb-uart | consola/login | Activo (console) |
| ttyS1-7 | 16550A Emulado | serial8250 | grupo dialout | Presentes pero no en uso |
| ttyGS0 | USB Gadget | g_serial | login | Activo |
| ttyUSB* | USB-UART | (no present) | N/A | No conectado |

### Puertos Libres para Comunicación
- **ttyS1-7**: Disponibles para el motor/placa externa (si tiene conexión física UART)
- **ttyGS0**: Disponible como interfaz USB (comunicación bidireccional USB)

### Console Mappings
- Kernel console: `ttyS0:115200`
- TTY para login: `ttyS0`, `ttyGS0`

### Hallazgo Crítico
La presencia de `ttyGS0` (USB Gadget Serial) activo sugiere que la A13 se comunica con la placa de motor vía USB como periférico (Device Mode), no como Host.
