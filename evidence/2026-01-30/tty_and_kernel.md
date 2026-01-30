# Evidencia: Puertos TTY y Mensajes del Kernel

**Fecha**: 2026-01-30  
**Objetivo**: Verificar qué puertos serie existen y qué dice el kernel sobre UART.

## 1.1) Puertos visibles en /dev

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /dev/ttyS* /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true'
```

**Salida**:
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

**Interpretación**:
- Los puertos **ttyS0–ttyS7** existen en `/dev/`.
- **ttyS0** tiene permisos más restrictivos (crw--w----): es la consola.
- **ttyS1–ttyS7** tienen permisos "dialout" (crw-rw----): accesibles para comunicación serie.
- **No hay ttyUSB o ttyACM**: no hay convertidores USB-serie reconocidos.

## 1.2) Alias estables en /dev/serial

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /dev/serial/by-id /dev/serial/by-path 2>/dev/null || true'
```

**Salida**:
```
(directorio vacío)
```

**Interpretación**:
- No hay alias estables (`by-id` / `by-path`): probablemente porque los puertos são internos (no USB).

## 1.3) Mensajes del kernel sobre UART/serial

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dmesg -T | grep -Ei "ttyS|ttyAMA|ttyACM|ttyUSB|uart|serial|sunxi" || true'
```

**Salida** (filtrado):
```
[Fri Jan 30 16:52:07 2026] Kernel command line: root=PARTUUID=023aa8cd-01 rootwait console=ttyS0,115200 panic=10 loglevel=4 
[Fri Jan 30 16:52:08 2026] sun5i-pinctrl 1c20800.pinctrl: initialized sunXi PIO driver
[Fri Jan 30 16:52:08 2026] Serial: 8250/16550 driver, 8 ports, IRQ sharing disabled
[Fri Jan 30 16:52:08 2026] printk: console [ttyS0] disabled
[Fri Jan 30 16:52:08 2026] 1c28400.serial: ttyS0 at MMIO 0x1c28400 (irq = 34, base_baud = 1500000) is a 16550A
[Fri Jan 30 16:52:08 2026] printk: console [ttyS0] enabled
[Fri Jan 30 16:52:08 2026] sunxi-wdt 1c20c90.watchdog: Watchdog enabled (timeout=16 sec, nowayout=0)
[Fri Jan 30 16:52:09 2026] usb 1-1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[Fri Jan 30 16:52:09 2026] usb 1-1.2: SerialNumber: 788CB533A81D
[Fri Jan 30 16:52:17 2026] systemd[1]: Created slice system-serial\x2dgetty.slice.
[Fri Jan 30 16:52:18 2026] g_serial gadget: Gadget Serial v2.4
[Fri Jan 30 16:52:18 2026] g_serial gadget: g_serial ready
```

**Interpretación**:
- **Serial driver cargado**: "Serial: 8250/16550 driver, 8 ports" → el kernel carga 8 puertos.
- **ttyS0 identificado**: "1c28400.serial: ttyS0 at MMIO 0x1c28400" → puerto 0 está en la dirección 0x1c28400.
- **ttyS0 como consola**: console=[ttyS0] enabled → ttyS0 es la consola del kernel.
- **USB gadget serie**: "g_serial gadget: g_serial ready" → hay un gadget serie USB, pero puede no estar usado.
- **No hay ttyAMA, ttyUSB, ttyACM**: son puertos UART directos, no conversores.

## 1.4) Consola del kernel

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /proc/cmdline | tr " " "\n" | grep -E "^console=" || true'
```

**Salida**:
```
console=ttyS0,115200
```

**Interpretación**:
- **ttyS0 es la consola del kernel** a 115200 baud.
- Esto significa que ttyS0 está "secuestrado" para debug/consola del sistema.
- Los demás puertos (ttyS1–ttyS7) están disponibles para aplicaciones como Klipper.

## Conclusión de esta sección

✅ **Los puertos serie existen en el sistema**:
- ttyS0–ttyS7 están presentes en `/dev/`.
- El driver 8250/16550 los reconoce.
- ttyS0 está dedicado a la consola del kernel.
- **ttyS1–ttyS7 están disponibles** para otras aplicaciones.

**Pregunta aún pendiente**: ¿Están todos estos puertos UART realmente habilitados en el Device Tree / script.bin?
→ Respuesta en `dt_uart_status.md`.
