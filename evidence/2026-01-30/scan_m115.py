#!/usr/bin/env python3
"""
Escaneo M115 - Identifica puerto Marlin
Sin dependencias externas (usa fcntl, termios, select)
"""
import os, sys, glob, time, fcntl, termios, select

def configure_serial(port, baud):
    try:
        fd = os.open(port, os.O_RDWR | os.O_NONBLOCK)
        attrs = termios.tcgetattr(fd)
        # [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
        attrs[2] &= ~(termios.CSIZE | termios.CSTOPB | termios.PARENB)  # 8N1
        attrs[2] |= termios.CS8
        # Mapear baud rate
        baud_map = {250000: termios.B115200,  # fallback
                    115200: termios.B115200, 57600: termios.B57600, 
                    19200: termios.B19200}
        attrs[4] = attrs[5] = baud_map.get(baud, termios.B115200)
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        return fd
    except:
        return None

ports = sorted(glob.glob("/dev/ttyS[1-7]"))
bauds = [250000, 115200, 57600, 19200]
hits = []

print("=== ESCANEO M115 ===")
for port in ports:
    for baud in bauds:
        sys.stdout.write(f"Testing {port} @ {baud} baud... ")
        sys.stdout.flush()
        fd = configure_serial(port, baud)
        if fd is None:
            print("ERR_OPEN")
            continue
        try:
            # Limpiar buffer
            os.read(fd, 4096)
            # Enviar M115
            os.write(fd, b"M115\n")
            time.sleep(0.3)
            # Leer respuesta
            response = b""
            while True:
                ready = select.select([fd], [], [], 0.1)[0]
                if not ready:
                    break
                try:
                    chunk = os.read(fd, 512)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            if b"FIRMWARE" in response or b"Marlin" in response:
                hits.append((port, baud, response[:300]))
                print(f"HIT! {response[:80].decode('latin1', 'ignore')}")
            else:
                print("No response")
        finally:
            os.close(fd)

print("\n=== RESULTADOS ===")
for port, baud, resp in hits:
    print(f"PORT: {port}, BAUD: {baud}")
    print(f"RESPONSE: {resp.decode('latin1', 'ignore')}")
