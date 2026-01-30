# Fuentes de Información y Enlaces Oficiales

## Documentación Oficial Allwinner A13

- **Datasheet Allwinner A13** (si está disponible)
  - Familia: Allwinner sun4i/sun5i
  - Información: Periféricos, direcciones de memoria, pin configuration
  - Fuente: Documentación del fabricante (requiere acceso)

## Documentación Olimex A13 SOM

- **Olimex A13-SOM** (hardware)
  - URL: https://www.olimex.com/Products/SOM/A13/
  - Información: Módulo, pines expuestos, conectores
  - Referencia: Pinout diagram, schematics

## Kernel Linux Allwinner

- **Kernel Linux sunxi**
  - Repositorio: https://github.com/linux-sunxi/
  - Información: Device tree source, drivers para serie/I2C/SPI/GPIO
  - Rama: Compatible con Allwinner A13

## Leapfrog/Creatr HS Documentation

- **Creatr HS Official** (información general sobre impresora)
  - Información: Especificaciones hardware, conectores
  - Nota: Datasheet del control board no disponible públicamente

## Klipper Firmware

- **Klipper 3D Printer Firmware**
  - URL: https://www.klipper3d.org/
  - Documentación: Configuración, protocolos MCU, debugging
  - Repositorio: https://github.com/Klipper3d/klipper

## Referencias USB y Gadget Serial

- **Linux USB Gadget Framework**
  - Documentación: Kernel USB gadget APIs
  - Módulo: `g_serial` (generic serial gadget)
  - Referencia: `drivers/usb/gadget/` en kernel source

## I2C en Linux

- **I2C Tools**
  - Herramienta: i2cdetect, i2cget, i2cset
  - Documentación: https://i2c.wiki.kernel.org/
  - Paquete: i2c-tools (en Debian)

## UART y Serial

- **Linux Serial Drivers**
  - Driver 8250: `drivers/tty/serial/8250/`
  - Driver dw-apb-uart: Designware APB UART
  - Referencia: Linux kernel serial documentation

## Formatos de Captura Utilizados

- **Device Tree Compiler (dtc)**
  - Herramienta: `dtc` (device-tree-compiler package)
  - Uso: Convertir `/proc/device-tree` a DTS para análisis
  - Referencia: https://devicetree.org/

---

## Notas sobre Disponibilidad

⚠️ **Datasheets del Fabricante**: Algunos documentos requieren registro o acceso especial
⚠️ **Esquemáticos Leapfrog**: No están públicamente disponibles (requieren contacto directo)
✓ **Documentación de Kernel**: Disponible públicamente en linux-sunxi
✓ **Klipper**: Documentación oficial disponible en sitio web

---

## Próximas Búsquedas Recomendadas

1. **Búsqueda local**: Verificar `/usr/share/doc`, `/usr/share/boards`, etc.
2. **Forum Olimex**: https://olimex.com/forum/ (búsqueda por puerto serie A13)
3. **LinuxCNC/Klipper**: Foros sobre configuración de A13 + Klipper
4. **Contacto directo**: Leapfrog/Creatr support para detalles de hardware motor

---

Actualizado: 2026-01-30
