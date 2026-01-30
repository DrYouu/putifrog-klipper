# Evidencia: Tipo de configuración de boot (Device Tree vs script.bin)

**Fecha**: 2026-01-30  
**Objetivo**: Detectar si el sistema usa Device Tree (DT) o script.bin/FEX (legacy).

## 2.1) Contenido de /boot

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -la /boot 2>/dev/null | head -50'
```

**Salida**:
```
total 45872
drwxr-xr-x  2 root root     4096 Jan 27 22:05 .
drwxr-xr-x 18 root root     4096 Oct  7  2024 ..
-rw-r--r--  1 root root     1950 Oct  7  2024 boot.cmd
-rw-r--r--  1 root root     2022 Oct  7  2024 boot.scr
-rw-r--r--  1 root root   191040 Jan 22 14:55 config-5.10.180-olimex
-rw-r--r--  1 root root 14995521 Jan 27 22:04 initrd.img-5.10.180-olimex
-rw-r--r--  1 root root 21616811 Jan 27 21:52 kernel.itb
-rw-r--r--  1 root root     3177 Jan 27 21:52 kernel.its
-rw-r--r--  1 root root  3557242 Jan 22 14:55 System.map-5.10.180-olimex
-rw-r--r--  1 root root      462 Jan 27 22:05 uEnv.txt
-rwxr-xr-x  1 root root  6574208 Jan 22 14:55 vmlinuz-5.10.180-olimex
```

**Interpretación**:
- ❌ **No hay script.bin**: no hay archivo `script.bin` (sería legacy FEX).
- ✅ **Hay kernel.itb**: archivo de Device Tree embebido (kernel.itb es una imagen ITB que incluye el kernel + DTB).
- ✅ **Hay boot.cmd/boot.scr**: scripts U-Boot que cargan kernel e inicializan.
- ℹ️ **No hay .dtb externo en /boot**: el DTB está dentro de kernel.itb.

## 2.2) ¿Existe /proc/device-tree?

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -la /proc/device-tree 2>/dev/null | head -30 || echo NO_PROC_DEVICE_TREE'
```

**Salida**:
```
lrwxrwxrwx 1 root root 29 Jan 30 17:51 /proc/device-tree -> /sys/firmware/devicetree/base
```

**Interpretación**:
- ✅ `/proc/device-tree` existe → el árbol DT está cargado en el kernel.
- Apunta a `/sys/firmware/devicetree/base` (ubicación estándar en sistemas con DT).

## 2.3) Modelo de placa (identidad DT)

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /proc/device-tree/model 2>/dev/null || echo NO_DTB_MODEL'
```

**Salida**:
```
(vacío / sin salida clara)
```

**Interpretación**:
- El nodo `/model` en el DTB podría estar vacío o no existir.
- No es un error crítico; lo importante es que el DT está presente y funcional.

## Conclusión

🎯 **El sistema usa Device Tree (DT), NO script.bin/FEX**

Evidencia:
1. No hay `script.bin` en `/boot`.
2. El kernel carga `kernel.itb` que contiene el DTB embebido.
3. `/proc/device-tree` existe y está vivo en el kernel.
4. Los comandos del kernel mencionan pinctrl de sunXi (típico de DT).

**Implicación para UART**:
- La configuración de UART se define en el DTB (Device Tree Blob) embebido en `kernel.itb`.
- Para cambiar UART, habría que recompilar el DTB o usar overlays (si están soportados).
- La verificación de qué UARTs están habilitados se hace en `dt_uart_status.md`.
