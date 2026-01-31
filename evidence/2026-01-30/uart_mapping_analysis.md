# Análisis: Mapeo UART A13 (DTB actual vs documentación Olimex)

**Fecha**: 2026-01-30  
**Fuente**: 
- Documentación oficial Olimex: `SOFTWARE/A13/A13-build/A13_olinuxino_Debian_kernel_3.4.90+_image_description.txt`
- DTB vivo en Olimex remota: `/proc/device-tree`
- Repo OLINUXINO-master

---

## Hallazgo clave de la documentación Olimex

```
UART3 - /dev/ttyS1
```

**Interpretación**: En la imagen oficial Olimex para A13, UART3 del chip está configurado y aparece como `/dev/ttyS1`.

---

## Mapeo teórico (A13 datasheet)

El chip Allwinner A13 tiene 4 UARTs:
- **UART0**: dirección MMIO 0x1c28000
- **UART1**: dirección MMIO 0x1c28400  
- **UART2**: dirección MMIO 0x1c28800
- **UART3**: dirección MMIO 0x1c28c00

---

## Lo que vemos en el DTB actual (2026-01-30)

| UART | Dirección    | DTB Status | Pinctrl | Kernel dice | ttyS asignado |
|------|--------------|------------|---------|-------------|---------------|
| UART0| 1c28000      | disabled   | Sí      | No mención  | (ninguno)     |
| UART1| 1c28400      | **okay**   | Sí      | ttyS0 @ 115200 | ttyS0 (consola)|
| UART2| 1c28800      | disabled   | Sí      | No mención  | (ninguno)     |
| UART3| 1c28c00      | disabled   | Sí      | No mención  | (ninguno)     |

---

## ¿Por qué discrepancia?

**Hipótesis**: La imagen oficial Olimex usaba kernel 3.4.90 (legacy, 2013–2015). Tu sistema usa **kernel 5.10.180** (mucho más reciente, con Device Tree moderno).

**Implicación**: El DTB en kernel 5.10 probablemente fue recompilado o es diferente del original Olimex.

---

## Documentación de MOD-GPS (evidencia adicional)

En `SOFTWARE/A13/MOD-GPS/README`:

```
The data is read on ttyAMA0 port. You should disable this port to use any UART modules.
...
where XXX is serial port.
For example: "/dev/ttyS0", "/dev/ttyAMA0", etc...
```

**Conclusión**: En sistemas antiguos Olimex, también mencionaban:
- `ttyAMA0` (puertos UART mapeados por driver ARM AMBA)
- `ttyS0` (puertos UART estándar 8250)

---

## Ahora: ¿Cuál UART está físicamente en el conector DEBUG?

### La wiki de Olimex dice:

> "**DEBUG-UART connector for console debug with USB-SERIAL-CABLE-F**"

**Problema**: No especifica cuál UART (0, 1, 2, 3) está en ese conector.

### Investigación en esquemáticos KiCAD

Tienes:
- `A13-OLinuXino-MICRO_Rev_C1.sch` (esquemático KiCAD)
- `A13-OLinuXino-MICRO_Rev_C1.pdf` (esquemático PDF)

**Necesito que hagas**: Abre el PDF con un lector PDF y busca:
1. **DEBUG connector** o **UART connector**
2. Pinout: ve a qué pines del A13 chip va TX/RX
3. En la hoja de datos del A13, verifica cuál UART usa esos pines

---

## Lo que puedo decir ahora (sin el esquemático)

### ✅ Certeza

1. **Kernel 5.10.180-olimex** carga un Device Tree que **solo habilita UART1** (serial@1c28400).
2. UART1 está asignado a **ttyS0** y usado como **consola del kernel** (115200 baud).
3. Los otros UART (0, 2, 3) están en estado `disabled` en el DTB.

### ❓ Incógnita

1. **¿Dónde está el conector DEBUG-UART físicamente?**
   - ¿En UART0, UART1, UART2 o UART3?
   - Respuesta: **En el esquemático/pinout**.

2. **¿Por qué solo UART1 está habilitado en este DTB?**
   - Posible razón: Fue la opción por defecto del compilador DTB.
   - O: Es el único que tiene hardware GPIO asignado correctamente.

---

## Plan para resolver

1. **Abre el PDF esquemático** de la A13-OLinuXino-MICRO (o A13-OLinuXino, la que uses).
2. **Busca "DEBUG UART"** o **"UART"** en el índice/buscar del PDF.
3. **Lee a qué pines van TX/RX** (ejemplo: PD2/PD3, o PA2/PA3, etc.).
4. **Verifica en A13 datasheet** qué UART usan esos pines.
5. **Reporta aquí**: "El DEBUG UART está en pines XYZ, que corresponden a UART0/1/2/3".
6. **Luego habilitamos ese UART en el DTB**.

---

## Resumen ejecutivo

| Pregunta | Respuesta actual | Fuente | Certeza |
|----------|------------------|--------|---------|
| ¿Cuántos UART están habilitados en DTB? | 1 (UART1) | DTB vivo | 100% |
| ¿Cuál UART es ttyS0? | UART1 (1c28400) | dmesg + DTB | 100% |
| ¿Dónde está el DEBUG-UART? | **DESCONOCIDO** | Esquemático (necesario) | 0% |
| ¿Qué UART habilitar para Klipper? | **Depende de dónde esté el cable** | Identificación física | — |

---

**Próximo paso**: Consulta el esquemático y dime los pines exactos del DEBUG-UART.
