import qrcode
import os

# Pedir datos al usuario
data = input("Ingresa el link: ")
nombre = input("Ingresa el nombre del archivo (sin .png): ")

# Limpiar nombre
nombre = nombre.strip().replace(" ", "_")

archivo = f"{nombre}.png"

# Evitar sobrescribir archivos
contador = 1
while os.path.exists(archivo):
    archivo = f"{nombre}_{contador}.png"
    contador += 1

# Crear y guardar QR
qr = qrcode.make(data)
qr.save(archivo)

print("QR generado y guardado como:", archivo)

# Abrir automáticamente (solo Windows)
os.startfile(archivo)