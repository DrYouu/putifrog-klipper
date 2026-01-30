# Evidencia: Estado de UART en Device Tree

**Fecha**: 2026-01-30  
**Objetivo**: Verificar qué UARTs están habilitados en el Device Tree y si tienen pinmux asignado.

## 3.1) Verificación de herramienta dtc

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'command -v dtc >/dev/null && echo DTC_OK || echo DTC_MISSING'
```

**Salida**:
```
DTC_OK
```

**Interpretación**:
- ✅ `dtc` (Device Tree Compiler) está disponible → podemos descompilar el DT vivo.

## 3.2) Extracción de DT: búsqueda de serial/uart/pinctrl/status

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dtc -I fs -O dts /proc/device-tree 2>/dev/null | grep -nEi "serial@|uart|pinctrl|status" | head -80'
```

**Salida** (filtrado, líneas clave):
```
52:             status = "disabled";
68:             uart2_pd_pins = "/soc/pinctrl@1c20800/uart2-pd-pins";
76:             nand_pins = "/soc/pinctrl@1c20800/nand-pins";
85:             mmc2_8bit_pins = "/soc/pinctrl@1c20800/mmc2-8bit-pins";
...
109:            uart0 = "/soc/serial@1c28000";
...
154:            uart1 = "/soc/serial@1c28400";
...
193:                    status = "disabled";    <-- serial@1c28000
215:                    status = "okay";
218:                    pinctrl-0 = <0x1c>;
220:                    pinctrl-names = "default";
228:                    status = "okay";
234:                    pinctrl-0 = <0x06>;
237:                    pinctrl-names = "default";
280:                    status = "okay";
287:                    pinctrl-0 = <0x0b>;
289:                    pinctrl-names = "default";
296:                    status = "disabled";
...
510:                    status = "disabled";    <-- serial@1c28800
514:                    status = "disabled";
...
585:                    status = "okay";        <-- serial@1c28400
589:                    status = "okay";
593:                    pinctrl-0 = <0x14>;
595:                    pinctrl-names = "default";
...
598:                    status = "disabled";    <-- serial@1c28c00
```

## 3.3) Análisis detallado de cada puerto serial

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dtc -I fs -O dts /proc/device-tree 2>/dev/null | grep -A 10 "serial@1c28" | head -100'
```

**Salida**:
```
serial@1c28000 {
        reg-io-width = <0x04>;
        compatible = "snps,dw-apb-uart";
        clocks = <0x02 0x3b>;
        status = "disabled";              <-- ❌ DESHABILITADO
        interrupts = <0x01>;
        phandle = <0x4d>;
        reg = <0x1c28000 0x400>;
        reg-shift = <0x02>;
};

serial@1c28800 {
        reg-io-width = <0x04>;
        compatible = "snps,dw-apb-uart";
        clocks = <0x02 0x3d>;
        status = "disabled";              <-- ❌ DESHABILITADO
        interrupts = <0x03>;
        phandle = <0x4f>;
        reg = <0x1c28800 0x400>;
        reg-shift = <0x02>;
};

serial@1c28400 {
        reg-io-width = <0x04>;
        compatible = "snps,dw-apb-uart";
        clocks = <0x02 0x3c>;
        status = "okay";                  <-- ✅ HABILITADO
        interrupts = <0x02>;
        phandle = <0x4e>;
        reg = <0x1c28400 0x400>;
        pinctrl-0 = <0x14>;               <-- ✅ PINMUX ASIGNADO
        reg-shift = <0x02>;
        pinctrl-names = "default";        <-- ✅ PINMUX ACTIVO
};

serial@1c28c00 {
        reg-io-width = <0x04>;
        compatible = "snps,dw-apb-uart";
        clocks = <0x02 0x3e>;
        status = "disabled";              <-- ❌ DESHABILITADO
        interrupts = <0x04>;
        phandle = <0x50>;
        reg = <0x1c28c00 0x400>;
        reg-shift = <0x02>;
};
```

## Tabla de estado de UART en Device Tree

| Puerto    | Dirección   | Registro              | Status      | Pinctrl-0 | Pinctrl-names | Interrupts | Estado Overall         |
|-----------|-------------|------------------------|-------------|-----------|---------------|------------|------------------------|
| UART0     | 1c28000     | serial@1c28000        | **disabled**| ❌ No      | ❌ No         | 0x01       | ❌ **NO HABILITADO**   |
| UART1     | 1c28400     | serial@1c28400        | **okay**    | ✅ Sí      | ✅ Sí         | 0x02       | ✅ **HABILITADO AQUÍ** |
| UART2     | 1c28800     | serial@1c28800        | **disabled**| ❌ No      | ❌ No         | 0x03       | ❌ **NO HABILITADO**   |
| UART3     | 1c28c00     | serial@1c28c00        | **disabled**| ❌ No      | ❌ No         | 0x04       | ❌ **NO HABILITADO**   |

## Mapeo: dirección MMIO → puerto ttyS

Según el kernel (`dmesg`):
- `1c28400.serial: ttyS0` → UART1 (dirección 1c28400) se reporta como ttyS0 (la consola).

En el DT:
- `serial@1c28400` tiene `status = "okay"` ✅
- Tiene pinctrl asignado ✅

En `/dev`:
- Existen ttyS0–ttyS7 (8 puertos).

**Conclusión del mapeo**:
- El puerto 1c28400 (UART1 en el DTB) está habilitado en DT → kernel lo activa como ttyS0 (consola).
- Los demás puertos UART (0, 2, 3) están deshabilitados en el DTB → el kernel no los activa, pero `/dev/ttyS*` existen como stubs sin backing hardware.

## Verificación de pinctrl disponibles en el DT

```bash
dtc -I fs -O dts /proc/device-tree 2>/dev/null | grep -E "uart[0-3].*pins" | head -20
```

Mencionados en el DT:
- `uart0_pg_pins` ← referencias a pinctrl para UART0
- `uart1_pe_pins` ← referencias a pinctrl para UART1
- `uart1_pg_pins` ← referencias a pinctrl para UART1
- `uart2_pd_pins` ← referencias a pinctrl para UART2
- `uart2-cts-rts-pd-pins` ← referencias a pinctrl para UART2
- `uart3_pg_pins` ← referencias a pinctrl para UART3
- `uart3_cts_rts_pg_pins` ← referencias a pinctrl para UART3

**Interpretación**:
- El DTB incluye definiciones de pinctrl para UART0/1/2/3.
- Pero solo el UART1 (serial@1c28400) está habilitado (`status = "okay"`).
- Los demás están `disabled`, por lo que sus pinctrl no se aplican.

## Conclusión global sobre UART/pinmux

| Aspecto                     | Hallazgo                                                        |
|-----------------------------|----------------------------------------------------------------|
| **Sistema de configuración**| Device Tree (DT) ✅                                              |
| **UART realmente habilitado**| Solo UART1 (`serial@1c28400`) → ttyS0 (consola) ✅              |
| **Pinmux del UART habilitado**| Sí, `pinctrl-0` y `pinctrl-names = "default"` asignados ✅      |
| **Otros UART (0, 2, 3)**   | Status = "disabled" en DT ❌                                     |
| **Pinctrl definiciones**    | Existen en DT para todos los UART, pero inactivas ❌            |
| **Solución para otros UART**| Habría que cambiar `status = "disabled"` → `status = "okay"` en DT + recompilar DTB |

## Implicación para Klipper

- **Klipper busca puertos serie en /dev/ttyS***.
- `/dev/ttyS0` está ocupado por la consola del kernel → **NO se puede usar para Klipper**.
- `/dev/ttyS1–ttyS7` existen como archivos, pero **solo ttyS1 (serial@1c28400) tiene backing hardware realmente activo**.
- **Los demás (ttyS2–ttyS7) son stubs del driver sin UART hardware habilitado detrás**.

**Riesgo**: si Klipper intenta usar ttyS2/S3/S4 (que no están en DT como "okay"), probablemente fallará o se colgará.

**Recomendación**: identificar cuál UART está físicamente conectado a la placa de control, y luego:
1. Si está en la lista deshabilitada (UART0/2/3): habilitar en DT.
2. Si es UART1: verificar por qué la consola está ahí (puede ser conflicto de uso).
