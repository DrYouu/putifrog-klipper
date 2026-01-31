#!/usr/bin/env python3
import os
import time
import fcntl
import termios
import struct

PORTS = ["ttyS1", "ttyS2", "ttyS3"]
BAUDRATES = [115200, 57600, 38400, 19200, 9600]
TIMEOUT = 2
CMD = b"M115\n"

# Mapa de baudrates a velocidades termios
BAUD_MAP = {
    115200: termios.B115200,
    57600: termios.B57600,
    38400: termios.B38400,
    19200: termios.B19200,
    9600: termios.B9600,
}

def get_status_flags(fd, baud):
    """Obtener flags termios actuales"""
    try:
        return termios.tcgetattr(fd)
    except:
        return None

def set_baud_raw(fd, baud):
    """Configurar baudrate sin librerías externas"""
    try:
        attrs = termios.tcgetattr(fd)
        # attrs[0] = iflag, [1] = oflag, [2] = cflag, [3] = lflag
        # [4] = ispeed, [5] = ospeed, [6] = cc
        
        cflag = attrs[2]
        cflag &= ~termios.CSIZE
        cflag |= termios.CS8
        cflag &= ~termios.CSTOPB  # 1 stop bit
        cflag &= ~termios.PARENB  # no parity
        cflag |= termios.CREAD | termios.CLOCAL  # enable read, local
        
        attrs[2] = cflag
        attrs[4] = BAUD_MAP.get(baud, termios.B115200)
        attrs[5] = BAUD_MAP.get(baud, termios.B115200)
        
        # Disable canonical mode and echo
        attrs[3] &= ~(termios.ICANON | termios.ECHO)
        
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        return True
    except Exception as e:
        return False

def test_port(port_name, baud):
    """Probar puerto único con baudrate especifico"""
    port_path = f"/dev/{port_name}"
    
    if not os.path.exists(port_path):
        return None, "NO EXISTE"
    
    try:
        # Abrir puerto
        fd = os.open(port_path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        
        # Configurar baudrate
        if not set_baud_raw(fd, baud):
            os.close(fd)
            return None, "STTY FALLÓ"
        
        # Cambiar a blocking mode temporal
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
        
        # Limpiar buffers
        termios.tcflush(fd, termios.TCIOFLUSH)
        
        # Enviar comando
        os.write(fd, CMD)
        
        # Esperar respuesta con timeout
        start = time.time()
        response = b""
        while time.time() - start < TIMEOUT:
            try:
                chunk = os.read(fd, 256)
                if chunk:
                    response += chunk
            except:
                time.sleep(0.01)
        
        os.close(fd)
        
        # Procesar respuesta
        try:
            clean = response.decode("utf-8", errors="ignore")
            clean = "".join(c for c in clean if c.isprintable() or c in "\n\r\t")
            clean = clean.strip()
            return clean if clean else "", "VACÍO" if not clean else "OK"
        except:
            return None, "DECODE ERROR"
            
    except Exception as e:
        return None, f"ERROR: {str(e)[:30]}"

# MAIN
print("=== UART MARLIN SCAN (Raw I/O) ===")
print()

results = []

for port_name in PORTS:
    for baud in BAUDRATES:
        response, status = test_port(port_name, baud)
        
        if response is not None and response:
            print(f"✓ {port_name} @ {baud:>6}: {response[:70]}")
            results.append((port_name, baud, response))
        elif status == "VACÍO":
            print(f"  {port_name} @ {baud:>6}: sin respuesta")
        else:
            print(f"✗ {port_name} @ {baud:>6}: {status}")

print()
print("=== RESUMEN ===")
if results:
    print(f"✓ {len(results)} puerto(s) con respuesta:")
    for port, baud, resp in results:
        print(f"  {port} @ {baud} baud: {resp[:60]}")
else:
    print("✗ Sin respuestas detectadas en ningún puerto/baudrate")
    print()
    print("Posibles causas:")
    print("  - Marlin no está conectado a puertos ttyS1-3")
    print("  - MCU habla por baudrate no probado (ej: 9600, 19200)")
    print("  - MCU no es accesible como /dev/ttyS* (USB, I2C, GPIO)")
    print("  - Marlin no responde a M115 en esta configuración")
