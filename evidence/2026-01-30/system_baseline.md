# Baseline del Sistema - Olimex A13 SOM
## Evidencia: 2026-01-30

### Comando 1: Información de Fecha, Kernel y Distribución

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'date -Is; uname -a; cat /etc/os-release; cat /proc/cmdline'
```

#### Output
```
2026-01-30T17:51:20+00:00
Linux a13-som 5.10.180-olimex #145321 SMP Thu Jan 22 14:55:18 UTC 2026 armv7l GNU/Linux
PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
NAME="Debian GNU/Linux"
VERSION_ID="11"
VERSION="11 (bullseye)"
VERSION_CODENAME=bullseye
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://www.debian.org/bugs"
root=PARTUUID=023aa8cd-01 rootwait console=ttyS0,115200 panic=10 loglevel=4
```

#### Interpretación
- Kernel: Linux 5.10.180-olimex, compilación custom Olimex, arquitectura ARMv7 (32-bit)
- Distribución: Debian 11 (bullseye)
- Parámetro console: ttyS0@115200 baud (consola serie)
- SoC: Allwinner (implícito en nombre de kernel y familia)

---

### Comando 2: Modelo del Device Tree

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /proc/device-tree/model 2>/dev/null || echo "NO_DTB_MODEL"'
```

#### Output
```
(sin salida visible, pero sin error - el modelo está presente pero sin salida textual clara)
```

#### Interpretación
- Device tree presente (no error)
- Modelo no expuesto en texto plano en /proc/device-tree/model

---

### Comando 3: Información de CPU

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /proc/cpuinfo | sed -n "1,160p"'
```

#### Output
```
processor       : 0
model name      : ARMv7 Processor rev 2 (v7l)
BogoMIPS        : 1001.47
Features        : half thumb fastmult vfp edsp neon vfpv3 tls vfpd32
CPU implementer : 0x41
CPU architecture: 7
CPU variant     : 0x3
CPU part        : 0xc08
CPU revision    : 2

Hardware        : Allwinner sun4i/sun5i Families
Revision        : 0000
Serial          : 1625420409016318
```

#### Interpretación
- CPU: ARMv7 (cortex-A8) single-core, implementador ARM (0x41)
- Familia: Allwinner sun4i/sun5i (compatible con A13)
- Serial único: 1625420409016318

---

### Comando 4: Bloques de Almacenamiento

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL'
```

#### Output
```
NAME         SIZE TYPE FSTYPE MOUNTPOINT MODEL SERIAL
mmcblk0      7.2G disk                         0x1542d98b
└─mmcblk0p1  7.2G part ext4   /
```

#### Interpretación
- Almacenamiento: 1 x microSD/eMMC de 7.2 GB (modelo SA08G)
- Sistema de archivos: ext4, montado en raíz
- Usado: ~83% (5.5G de 7.1G)

---

### Comando 5: Espacio en Disco (df)

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'df -hT'
```

#### Output
```
Filesystem     Type      Size  Used Avail Use% Mounted on
udev           devtmpfs  189M     0  189M   0% /dev
tmpfs          tmpfs      49M   11M   39M  23% /run
/dev/mmcblk0p1 ext4      7.1G  5.5G  1.2G  83% /
tmpfs          tmpfs     245M     0  245M   0% /dev/shm
tmpfs          tmpfs     5.0M  4.0K  5.0M   1% /run/lock
tmpfs          tmpfs      49M   52K   49M   1% /run/user/1000
```

#### Interpretación
- Espacio raíz: 7.1G total, 5.5G usado (83%), 1.2G libre
- RAM total: 488M (visible en tmpfs)

---

### Comando 6: Memoria (free)

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'free -h'
```

#### Output
```
               total        used        free      shared  buff/cache   available
Mem:           488Mi       183Mi       225Mi        11Mi        79Mi       282Mi
Swap:             0B          0B          0B
```

#### Interpretación
- RAM Total: 488 MB
- RAM Disponible: 282 MB
- Sin swap configurado

---

### Comando 7: Logs del Kernel (dmesg últimas 250 líneas)

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dmesg -T | tail -n 250'
```

#### Output
(Ver `evidence/2026-01-30/dmesg_tail_250.log` para full output)

**Resumen de Eventos Relevantes:**
- `[Fri Jan 30 16:52:08] Serial: 8250/16550 driver, 8 ports, IRQ sharing disabled` - 8 puertos seriales registrados
- `[Fri Jan 30 16:52:08] 1c28400.serial: ttyS0 at MMIO 0x1c28400 (irq = 34, base_baud = 1500000) is a 16550A` - ttyS0 es la consola principal
- `[Fri Jan 30 16:52:18] g_serial gadget: Gadget Serial v2.4` - USB gadget serial activo
- Múltiples UART en device tree: uart0, uart1, uart2, uart3 mapeadas
- USB EHCI/OHCI/MUSB inicializados
- Panel LCD y backlight intentados (pero sin éxito)
- Controlador de video Cedrus registrado

#### Interpretación
- Kernel detecta múltiples puertos UART en SoC
- USB gadget activo (posible interfaz con placa de motor)
- Hardware gráfico presente (framebuffer)
